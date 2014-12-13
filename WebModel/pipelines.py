# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#python库
import sqlite3
import re
from scrapy import log
from urlparse import urlparse

from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder

#自定义的库
from WebModel.items import PageItem, RulesetItem
# 数据库操作 
from WebModel.database.databasehelper import getCliInstance
# [bloomfilter库,用以查重](https://github.com/jaybaird/python-bloomfilter/)
from pybloom import BloomFilter
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import domain_getter, TYPE_DOMAIN, TYPE_IP
# scrapy-redis 的pipeline
import WebModel.utils.scrapy_redis.connection as connection
from WebModel.utils.rediskeys import domains_key, related_domains_key

class RedisPipeline(object):
	"""Pushes serialized item into a redis list/queue"""

	def __init__(self, server):
		# redis server
		self.server = server
		# 用来判断是否重复出现
		allowed = [
			"qq.com",
			"163.com",
			"people.com.cn",
			"xinhuanet.com",
			"cntv.cn",
			"ifeng.com",
			"hexun.com",
			"sina.com.cn",
			"sohu.com",
			"dbw.cn",
		]
		self.bloom_domain_filter = BloomFilter(capacity=32)
		for a in allowed:
			self.bloom_domain_filter.add(a)

		# 正则过滤, 一些博客
		self.qzone_filter = re.compile(r"^http://.*\.qzone\.qq\.com")
		self.wangyiblog_filter = re.compile(r"^http://.*\.blog\.163\.com")
		self.hexunblog_filter = re.compile(r"^http://.*\.blog\.hexun\.com")
		self.sohublog_filter = re.compile(r"http://.*\.blog\.sohu\.com")
		self.sohui_filter = re.compile(r"http://.*\.i\.sohu\.com")

		self.bloom_domain_vec = BloomFilter(capacity=1<<16, error_rate=0.001)
		self.bloom_netloc_vec = BloomFilter(capacity=1<<16, error_rate=0.001)

	@classmethod
	def from_crawler(cls, crawler):
		settings = crawler.settings
		server = connection.from_settings(settings)
		pipe = cls(server)
		pipe.settings = settings
		pipe.crawler = crawler
		return pipe

	def process_item(self, item, spider):
		return deferToThread(self._process_item, item, spider)

	def _process_item(self, item, spider):
		if isinstance(item, RulesetItem):
			self._process_ruleset(item, spider)
		elif isinstance(item, PageItem):
			self._process_page(item, spider)
		return item

	def _process_ruleset(self, item, spider):
		if item['update']:
			if item['domain'] in self.bloom_domain_vec:
				spider.log("BloomFilter 判断错误!域名%s未出现过"%item['domain'], level=log.WARNING)
			# 新域名,建立域名记录
			#redis数据库
			self.server.hset(domains_key%item['domain'], 'indegree', 1)
			self.server.hset(domains_key%item['domain'], 'outdegree', 0)
			#sqlite3数据库
			# self.dbcli.insertDomain(item['domain'])

			spider.log("爬取到新域名: "+item['domain'], level=log.INFO)

			# 把robots.txt内容存储进数据库
			if item['ruleset']:
				#redis数据库
				self.server.hset(domains_key%item['domain'], 'ruleset', item['ruleset'])
				#sqlite3数据库
				# self.dbcli.insertRuleset(item['ruleset'], item['domain'])

				spider.log("爬取到域名的robots规则: "+item['domain'], level=log.INFO)

	def _process_page(self, item, spider):
		# 记录爬取过此网址
		self.server.rpush(spider.URL_VISITED_KEY, item['url'])
		
		domain, ret_type = domain_getter.get_domain(item['url'])
		if not self.bloom_domain_vec.add(domain):
			self._initRelateDomain(domain, spider)
			if not self.server.exists(domains_key%domain):
				self._initGlobalDomain(domain)

		for link in item['links']:

			if self._isBlogLink(link):
				self.server.rpush(spider.BLOG_IGNORE_KEY, link)
				continue

			link_domain, ret_type = domain_getter.get_domain(link)
			# 判断域名是否和当前爬取域名D0相同
			if link_domain == spider.CRAWLING_DOMAIN:
				# D0的size+1
				self.server.hincrby(domains_key%link_domain, 'size', 1)
				self.server.hincrby(related_domains_key%(spider.CRAWLING_DOMAIN,domain), 'size', 1)
				# 判断其netloc是否出现过
				netloc = urlparse(link).netloc
				if not self.bloom_netloc_vec.add(netloc):
					# 未出现过,网页进入队列
					self.server.rpush(spider.URL_QUEUE_KEY, "http://"+netloc)
			else:# 不同,则判断域名是否已经出现过
				if self.bloom_domain_vec.add(link_domain):
					# 已出现过,对应的记录D1入度+1
					self.server.hincrby(domains_key%link_domain, 'indegree', 1)
					self.server.hincrby(related_domains_key%(spider.CRAWLING_DOMAIN,link_domain), 'indegree', 1)
				else:
					# 没出现过,则Domain中增加记录D1,D1记录入度初始化为1,出度初始化为0;D0出度+1
					self._initGlobalDomain(link_domain)
					self.server.hincrby(domains_key%domain, 'outdegree', 1)

					self._initRelateDomain(link_domain, spider)
					self.server.hincrby(related_domains_key%(spider.CRAWLING_DOMAIN,link_domain), 'outdegree', 1)

		for link in item['refused_links']:
			spider.log(link+" refuse by robots.txt", level=log.INFO)
			self.server.rpush(spider.ROBOT_REFUSED_KEY, link)

	def _initGlobalDomain(self, domain):
		key = domains_key%domain
		self._raw_init_domain(key)

	def _initRelateDomain(self, domain, spider):
		key = related_domains_key%(spider.CRAWLING_DOMAIN, domain)
		self._raw_init_domain(key)

	def _raw_init_domain(self, key):
		self.server.hset(key, 'indegree', 0)
		self.server.hset(key, 'outdegree', 0)
		self.server.hset(key, 'size', 1)

	def _isBlogLink(self,link):
		# qq 空间个性域名,过滤
		if self.qzone_filter.match(link):
			return True
		
		# 网易博客个性域名,过滤
		elif self.wangyiblog_filter.match(link):
			return True

		# 和讯blog,过滤
		elif self.hexunblog_filter.match(link):
			return True

		# 搜狐blog、个人展示页,过滤
		elif self.sohublog_filter.match(link) or self.sohui_filter.match(link):
			return True

		return False
