# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 抓取的url
	url = scrapy.Field()
	# 列表, 这个domain对应的robots规则
	rules = scrapy.Field()
	# 标题
	title = scrapy.Field()
	# 其他url连接
	links = scrapy.Field()
