# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log, Request

# python库
# [url解析函数 urlparse](https://docs.python.org/2/library/urlparse.html)
from urlparse import urlparse

# 自定义的库
from WebModel.items import PageItem
# [robots.txt解析库(进行过修改)](http://nikitathespider.com/python/rerp/)
from WebModel.utils.robotexclusionrulesparser import RobotExclusionRulesParser as RobotsParser
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import PublicSuffixList
# [bloomfilter库,用以查重]()
from pybloom import BloomFilter

class SohuSpider(CrawlSpider):
	name = 'jayson'
	allowed_domains = ['*',]
	start_urls = ['http://1.jaysonhwang.sinaapp.com',]
	# rules = [Rule(LinkExtractor('/()'),
	#			 follow=True,
	# 			 callback='parse'),
	# 		]

	def __init__(self):
		CrawlSpider.__init__(self)
		# 用来解析robots.txt
		self.robotsparser = RobotsParser()
		# 用来解析url获取域名
		self.domaingetter = PublicSuffixList()
		self.bloom_vec = BloomFilter(capacity=10000, error_rate=0.001)

	def parse(self, response):
		item = PageItem()
		cnt = {
			'new':0,
			'appeared':0,
			'js':0,
		}

		# 解析url,获取域名
		netloc = urlparse(response.url).netloc
		domain = self.domaingetter.get_public_suffix(netloc)

		# 检查这个域名是否在数据库中


		# 使用xpath获取内容
		item['url'] = response.url
		item['title'] = response.xpath('/html/head/title').extract()[0]
		item['links'] = []
		for link in response.xpath('//a/@href').extract() :
			# 判断超链接内容是否为一个合法网址/相对网址
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
					# yield Request(link, callback=self.parse)
				else :
					cnt['appeared'] += 1
			else :
				msg = '%s : not a url'%(link,)
				# self.log(msg, level=log.DEBUG)

		msg = 'crwal in %s : %s'%(item['url'], cnt)
		self.log(msg, level=log.INFO)
		# log.msg(repr(item).decode("unicode-escape") + '\n', level=log.INFO, spider=self)

		yield item
