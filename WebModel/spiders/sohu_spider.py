# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log

# from bs4 import BeautifulSoup
from WebModel.items import PageItem

class SohuSpider(CrawlSpider):
	name = 'sohu'
	allowed_domains = ['news.sohu.com',]
	start_urls = ['http://news.sohu.com/20141103/n405702335.shtml',]
	# rules = [Rule(LinkExtractor('/()'),
	#			 follow=True,
	# 			 callback='parse'),
	# 		]

	def parse(self, response):
		item = PageItem()
		# 使用xpath获取内容
		item['url'] = response.url
		item['name'] = response.xpath('/html/head/meta[@name="keywords"]/@content').extract()[0]
		item['links'] = []
		for link in response.xpath('//a/@href').extract() :
			if link.startswith('http://'):
				item['links'].append(link)
			else :
				msg = '%s : not a url'%(link,)
				log.msg(msg, level=log.DEBUG, spider=self)
		msg = 'crwal %4d urls in %s'%(len(item['links']), item['url'])
		log.msg(msg, level=log.INFO, spider=self)
		# log.msg(repr(item).decode("unicode-escape") + '\n', level=log.INFO, spider=self)
		# soup = BeautifulSoup(response.body)

		return item
