# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#python库
import sqlite3
from scrapy import log

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
from WebModel.utils.rediskeys import url_queue_key, domains_key

class RedisPipeline(object):
	"""Pushes serialized item into a redis list/queue"""

	def __init__(self, server):
		# redis server
		self.server = server
		# 用来判断是否重复出现
		self.bloom_vec = BloomFilter(capacity=1<<32, error_rate=0.001)

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
			if item['update']:
				# 新域名,建立域名记录
				#redis数据库
				self.server.hset(domains_key+':'+item['domain'], 'indegree', 1)
				self.server.hset(domains_key+':'+item['domain'], 'outdegree', 0)

				#sqlite3数据库
				# self.dbcli.insertDomain(item['domain'])

				spider.log("Spot New Domain:"+item['domain'], level=log.INFO)

				# 把robots.txt内容存储进数据库
				if item['ruleset']:
					#redis数据库
					self.server.hset(domains_key+':'+item['domain'], 'ruleset', item['ruleset'])
					#sqlite3数据库
					# self.dbcli.insertRuleset(item['ruleset'], item['domain'])

					spider.log("Insert Ruleset to Domain:"+item['domain'], level=log.INFO)

		elif isinstance(item, PageItem):
			newlinks, oldlinks = [], []
			for link in item['links']:
				domain = domain_getter.get_domain(link)
				if not self.bloom_vec.add(link) :
					# 返回False,bloomfilter判定未出现过
					newlinks.append( (link, domain) )
				else :
					# 返回True,bloomfilter判定已经出现过
					oldlinks.append( (link, domain) )

			#redis数据库
			self.updateInfo(self.server, item, newlinks, oldlinks, spider)
			#sqlite3数据库
			# getCliInstance().updateInfo(item, newlinks, oldlinks)
		return item

	def updateInfo(self, server, item, newlinks, oldlinks, spider):
		pipe = server.pipeline()
		domain = domain_getter.get_domain(item['url'])
		server.hincrby(domains_key+':'+domain, 'outdegree', len(item['links']))
		# 对该网页中所有链接涉及的记录进行更新
		# 外部判断未出现过的链接
		for link, domain in newlinks:
			server.hset(domains_key+':'+domain, 'indegree', 1)
			server.hset(domains_key+':'+domain, 'outdegree', 0)
			server.rpush(url_queue_key, link)
		# 外部判断出现过的链接
		for link, domain in oldlinks:
			# 对对应的domain记录入度增加
			server.hincrby(domains_key+':'+domain, 'indegree', 1)
		pipe.execute()


