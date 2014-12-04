# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log, Request

# python库
# [url解析函数 urlparse](https://docs.python.org/2/library/urlparse.html)
from urlparse import urlparse

# 自定义的库
from WebModel.items import PageItem, RulesetItem
# [robots.txt解析库(进行过修改)](http://nikitathespider.com/python/rerp/)
from WebModel.utils.robotexclusionrulesparser import RobotExclusionRulesParser as RobotsParser
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import PublicSuffixList

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
		# 用来解析url获取域名
		self.domaingetter = PublicSuffixList()

	def parse(self, response):
		item = PageItem()
		cnt = {
			'new':0,
			'appeared':0,
			'js':0,
		}
		# 判断url是否被robots.txt内规则允许
		robotsparser, rulesetItem = self.getRuleset(response)
		# 把rulesetItem送到pipeline
		yield rulesetItem

		# 使用xpath获取内容
		item['url'] = response.url
		item['title'] = response.xpath('/html/head/title').extract()[0]
		item['links'] = []
		for link in response.xpath('//a/@href').extract() :
			# 判断超链接内容是否为一个合法网址/相对网址
			if link.startswith('http://') :
				# yield Request(link, callback=self.parse)
				pass
			elif link.startswith('/') :
				# 把网址补全,再yield请求
				# yield Request(link, callback=self.parse)
				pass
			else :
				msg = '%s : not a url'%(link,)
				# self.log(msg, level=log.DEBUG)

		msg = 'crwal in %s : %s'%(item['url'], cnt)
		self.log(msg, level=log.INFO)
		# log.msg(repr(item).decode("unicode-escape") + '\n', level=log.INFO, spider=self)

		yield item

	def getRuleset(self, response):
		robotsparser = RobotsParser()

		rulesetItem = RulesetItem
		# 解析url,获取域名
		netloc = urlparse(response.url).netloc
		domain = self.domaingetter.get_public_suffix(netloc)
		# 检查这个域名是否在数据库中
		exist, ruleset = dbcli.robotsrulesetOfDomain(domain)
		if not exist:
			# 从网络读取robots.txt文件
			#ruleset = ''
			pass
		else :
			# 重新解析robots.txt
			pass
		rulesetItem['domain'] = domain
		rulesetItem['ruleset'] = ruleset

		return (robotsparser, rulesetItem)
