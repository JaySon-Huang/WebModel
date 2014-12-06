# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#python库
import sqlite3
from scrapy import log
from urlparse import urlparse

from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder

#自定义的库
from WebModel.items import PageItem, RulesetItem
# 数据库操作 
from WebModel.database.databasehelper import getCliInstance
# [bloomfilter库,用以查重](https://github.com/jaybaird/python-bloomfilter/)
from WebModel.utils.pybloom import BloomFilter
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import domain_getter
# scrapy-redis 的pipeline
import WebModel.utils.scrapy_redis.connection as connection
from WebModel.utils.rediskeys import url_queue_key, domains_key, url_ignore_key, url_visited_key

class RedisPipeline(object):
	"""Pushes serialized item into a redis list/queue"""

	def __init__(self, server):
		# redis server
		self.server = server
		# 用来判断是否重复出现
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
		newlinks, oldlinks = [], []
		for link in item['links']:
			domain = domain_getter.get_domain(link)
			if not self.bloom_domain_vec.add(domain) :
				# 返回False,bloomfilter判定未出现过
				newlinks.append( (link, domain) )
			else :
				# 返回True,bloomfilter判定已经出现过
				oldlinks.append( (link, domain) )

		#redis数据库
		self._updateInfo(self.server, item, newlinks, oldlinks, spider)
		#sqlite3数据库
		# getCliInstance().updateInfo(item, newlinks, oldlinks)

	def _updateInfo(self, server, item, newlinks, oldlinks, spider):
		self._updateCurPage(server, item, spider)
		self._updateOutLink(server, newlinks, oldlinks, spider)


	def _updateCurPage(self, server, item, spider):
		server.sadd(url_visited_key, item['url'])
		netloc = urlparse(item['url']).netloc
		domain = domain_getter.get_domain(item['url'])
		try:
			self.bloom_domain_vec.add(domain)
			self.bloom_netloc_vec.add(netloc)
		except IndexError:
			# BloomFilter满了
			spider.log("BloomFilter is at the capacity.", level=log.ERROR)
		server.hincrby(domains_key%domain, 'outdegree', len(item['links']))

		i = int(server.hget(domains_key%domain, 'outdegree'))
		spider.log('outdegree of %s: %d'%(domain, i), level=log.INFO)

	def _updateOutLink(self, server, newlinks, oldlinks, spider):
		# 对该网页中所有链接涉及的记录进行更新
		# 外部判断未出现过的链接
		pipe = server.pipeline()
		for link, domain in newlinks:

			if server.exists(domains_key%domain):
				spider.log(u"判断失误,%s曾出现"%domain, level=log.CRITICAL)
				continue
			pipe.hset(domains_key%domain, 'indegree', 1)
			pipe.hset(domains_key%domain, 'outdegree', 0)

			netloc = urlparse(link).netloc
			# spider.log('Netloc <%s> from <%s>'%(netloc, link))

			try:
				isAppeared = self.bloom_netloc_vec.add(netloc)
			except IndexError:
				# BloomFilter满了
				spider.log("BloomFilter is at the capacity.", level=log.ERROR)
				isAppeared = False

			if not isAppeared:
				# 去除端口号, 以‘.’分割
				parts = netloc.split(':')[0].split('.')
				if len(parts) <= 3:
					spider.log("Spot new netloc: %s"%netloc, level=log.DEBUG)
					pipe.rpush(url_queue_key, link)
				elif parts[-1] == 'cn' and len(parts) <= 4 :
					spider.log("Spot new netloc: %s"%netloc, level=log.DEBUG)
					pipe.rpush(url_queue_key, link)
				elif parts[0] == 'www' and len(parts) <= 4 :
					spider.log("Spot new netloc: %s"%netloc, level=log.DEBUG)
					pipe.rpush(url_queue_key, link)
				else:
					self._drop(link, spider, pipe, '%s seems is NOT new netloc'%netloc)
			else :
				# spider.log("不再爬取%s上的网站:"%netloc, level=log.DEBUG)
				self._drop(link, spider, pipe, None)
				pass
		pipe.execute()

		pipe = server.pipeline()
		# 外部判断出现过的链接
		for link, domain in oldlinks:
			# 对对应的domain记录入度增加
			pipe.hincrby(domains_key%domain, 'indegree', 1)
		pipe.execute()
	def _drop(self, link, spider, pipe, reason):
		pipe.sadd(url_ignore_key, link)
		if reason:
			spider.log(reason, level=log.INFO)

