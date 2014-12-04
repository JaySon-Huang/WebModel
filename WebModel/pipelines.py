# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#python库
import sqlite3
# [url解析函数 urlparse](https://docs.python.org/2/library/urlparse.html)
from urlparse import urlparse
from scrapy import log

#自定义的库
from WebModel.items import PageItem, RulesetItem
# 数据库操作 
from WebModel.database.databasehelper import getCliInstance
# [bloomfilter库,用以查重](https://github.com/jaybaird/python-bloomfilter/)
from WebModel.utils.pybloom import BloomFilter
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import PublicSuffixList

class WebModelPipeline(object):

	def __init__(self):
		# 用来判断是否重复出现
		self.bloom_vec = BloomFilter(capacity=10000, error_rate=0.001)

	def process_item(self, item, spider):
		if isinstance(item, RulesetItem):
			if item['update']:
				# 新域名,建立域名记录
				self.dbcli.insertDomain(item['domain'])
				spider.log("Spot New Domain:"+item['domain'], level=log.INFO)

				# 把robots.txt内容存储进数据库
				if item['ruleset']:
					self.dbcli.insertRuleset(item['ruleset'], item['domain'])
					spider.log("Insert Ruleset to Domain:"+item['domain'], level=log.INFO)
		elif isinstance(item, PageItem):
			newlinks, oldlinks = [], []
			domain_getter = PublicSuffixList()
			for link in item['links']:
				domain = domain_getter.get_public_suffix(urlparse(link).netloc)
				if not self.bloom_vec.add(link) :
					# 返回False,bloomfilter判定未出现过
					newlinks.append( (link, domain) )
				else :
					# 返回True,bloomfilter判定已经出现过
					# 对于Website中已经有记录的，增加其入度
					oldlinks.append( (link, domain) )
			getCliInstance().updateInfo(item, newlinks, oldlinks)

	def __del__(self):
		getCliInstance().close()

