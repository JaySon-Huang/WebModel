# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3


# [bloomfilter库,用以查重]()
from pybloom import BloomFilter
# 
from WebModel.database.databasehelper import dbcli

class WebModelPipeline(object):

	def __init__(self):
		# 用来判断是否重复出现
		self.bloom_vec = BloomFilter(capacity=10000, error_rate=0.001)


	def process_item(self, item, spider):
		# 新域名,建立域名记录
		dbcli.insertDomain(domain)
		# 把robots.txt内容存储进数据库
		dbcli.insertRuleset(ruleset, domain)
		# bloomfilter判定未出现过
		if not self.bloom_vec.add(link) :
			item['links'].append(link)
			cnt['new'] += 1
			dbcli.insertWebsite(link)
		else :
			cnt['appeared'] += 1
			# self.log('%s have appeared in early time'%(link,), level=log.DEBUG)
		# 对于Website中已经有记录的，增加其入度
		# 存储Website中未记录的网址，根据urls算出其出度\
		# 建立与Rule
		return item

	def __del__(self):
		self.cx.commit()
		self.cx.close()

