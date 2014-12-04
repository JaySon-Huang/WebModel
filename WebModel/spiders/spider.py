# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log, Request

#python库
# [url解析函数 urlparse](https://docs.python.org/2/library/urlparse.html)
from urlparse import urlparse

#自定义的库
from WebModel.items import PageItem, RulesetItem
# [robots.txt解析库(进行过修改)](http://nikitathespider.com/python/rerp/)
from WebModel.utils.robotexclusionrulesparser import RobotExclusionRulesParser as RobotsParser
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import PublicSuffixList
# 数据库操作 
from WebModel.database.databasehelper import getCliInstance

class WebModelSpider(CrawlSpider):
	name = 'jayson'
	allowed_domains = []
	start_urls = ['http://www.qq.com',]
	# rules = [Rule(LinkExtractor('/()'),
	#			 follow=True,
	# 			 callback='parse'),
	# 		]

	def __init__(self):
		CrawlSpider.__init__(self)
		# 用来解析robots.txt
		# 用来解析url获取域名
		self.domaingetter = PublicSuffixList()
		for url in WebModelSpider.start_urls:
			import sqlite3
			try:
				domain = self.domaingetter.get_public_suffix(urlparse(url).netloc)
				getCliInstance().insertWebsite(url, domain)
			except sqlite3.IntegrityError:
				getCliInstance().rollback()

	def parse(self, response):
		# 解析url,获取域名
		netloc = urlparse(response.url).netloc
		domain = self.domaingetter.get_public_suffix(netloc)

		# 检查并获取domain对应的robots内容
		# robotsparser用以判断url是否被robots.txt内规则允许
		robotsparser, rulesetItem = self.getRuleset(domain)
		# 把rulesetItem送到pipeline
		yield rulesetItem

		pageItem = PageItem()
		# 使用xpath获取内容
		pageItem['url'] = response.url
		pageItem['title'] = response.xpath('/html/head/title/text()').extract()[0]
		print pageItem['title']
		pageItem['links'] = []
		# 把所有<a>标签的超链接提取出来
		for link in response.xpath('//a/@href').extract() :
			# 判断超链接内容是否为一个合法网址/相对网址
			if link.startswith('http://') :
				pageItem['links'].append(link)
				# robots判定
				# if not robotsparser or robotsparser.is_allowed('*', link):
				# 	pageItem['links'].append(link)
				# 	yield Request(link, callback=self.parse)
			elif link.startswith('/') :
				# 相对定位,把网址补全,再yield请求
				link = "http://"+ netloc + link
				pageItem['links'].append(link)
				# robots判定
				# if not robotsparser or robotsparser.is_allowed('*', link) :
				# 	pageItem['links'].append(link)
				# 	yield Request(link, callback=self.parse)
			else :
				# 不符合以上两种,一般为javascript函数
				# msg = '%s : not a url'%(link,)
				# self.log(msg, level=log.DEBUG)
				pass

		msg = 'crwal %d links from %s.'%(
			len(pageItem['links']), pageItem['url'])
		self.log(msg, level=log.INFO)
		# log.msg(repr(pageItem).decode("unicode-escape") + '\n', level=log.INFO, spider=self)

		yield pageItem

	def getRuleset(self, domain):
		robotsparser = RobotsParser()
		rulesetItem = RulesetItem()

		# 检查这个域名是否在数据库中
		exist, ruleset = getCliInstance().robotsrulesetOfDomain(domain)
		if not exist:
			# 从网络读取robots.txt文件
			robotsURL = "http://www."+domain+"/robots.txt"
			self.log("fetching robots.txt from "+robotsURL, level=log.INFO)
			if robotsparser.fetch(robotsURL):
				ruleset = str(robotsparser)
				self.log("Successfully parse "+robotsURL, level=log.INFO)
			else:
				ruleset = ''
				self.log("robots.txt NOT found.")
			# 标记让pipeline更新数据库内容
			rulesetItem['update'] = True
		else :
			self.log("resuming robots.txt of %s from database."%(domain), level=log.INFO)
			if ruleset:
				# 重新解析robots.txt
				robotsparser.parse(ruleset)
			else:
				robotsparser = None
			# 标记让pipeline不处理这个item
			rulesetItem['update'] = False

		rulesetItem['domain'] = domain
		rulesetItem['ruleset'] = ruleset

		return (robotsparser, rulesetItem)
