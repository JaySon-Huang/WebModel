# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PageItem(scrapy.Item):
    # 抓取的url
	url = scrapy.Field()
	# 标题
	title = scrapy.Field()
	# 其他url连接, len(links)添加到对于domain的出度信息
	links = scrapy.Field()
	# 被robots.txt拒绝抓取的links
	refused_links = scrapy.Field()

class RulesetItem(scrapy.Item):
	# 对应的domain
	domain = scrapy.Field()
	# ruleset内容
	ruleset = scrapy.Field()
	# 是否需要更新
	update = scrapy.Field()
