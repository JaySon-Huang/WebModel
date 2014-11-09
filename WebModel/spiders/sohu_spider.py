# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log, Request

from WebModel.items import PageItem
from pybloom import BloomFilter

class SohuSpider(CrawlSpider):
	name = 'sohu'
	allowed_domains = ['jaysonhwang.com',]
	start_urls = ['http://jaysonhwang.com',]
	# rules = [Rule(LinkExtractor('/()'),
	#			 follow=True,
	# 			 callback='parse'),
	# 		]

	def __init__(self):
		CrawlSpider.__init__(self)
		self.bloom_vec = BloomFilter(capacity=10000, error_rate=0.001)

	def parse(self, response):
		item = PageItem()
		cnt = {
			'new':0,
			'appeared':0,
			'js':0,
		}
		# 使用xpath获取内容
		item['url'] = response.url
		item['name'] = response.xpath('/html/head/meta[@name="keywords"]/@content').extract()[0]
		item['links'] = []
		for link in response.xpath('//a/@href').extract() :
			if link.startswith('http://') :
				# bloomfilter判定未出现过
				if not self.bloom_vec.add(link) :
					item['links'].append(link)
					cnt['new'] += 1
					yield Request(link, callback=self.parse)
				else :
					cnt['appeared'] += 1
					# self.log('%s have appeared in early time'%(link,), level=log.DEBUG)
			elif link.startswith('/') :
				link = 'http://jaysonhwang.com'+link
				if not self.bloom_vec.add(link) :
					item['links'].append(link)
					cnt['new'] += 1
					yield Request(link, callback=self.parse)
				else :
					cnt['appeared'] += 1
			else :
				msg = '%s : not a url'%(link,)
				# self.log(msg, level=log.DEBUG)

		msg = 'crwal in %s : %s'%(item['url'], cnt)
		self.log(msg, level=log.INFO)
		# log.msg(repr(item).decode("unicode-escape") + '\n', level=log.INFO, spider=self)

		yield item
