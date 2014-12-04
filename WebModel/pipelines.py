# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from WebModel.database.databasehelper import DatabaseHelper

class WebModelPipeline(object):

	def process_item(self, item, spider):
		# 对于Website中已经有记录的，增加其入度
		# 存储Website中未记录的网址，根据urls算出其出度\
		# 建立与Rule
		return item

	def __del__(self):
		self.cx.commit()
		self.cx.close()

