# -*- coding: utf-8 -*-

from scrapy import log
from scrapy.selector import Selector
from scrapy.spider import Spider

from urlparse import urlparse

#自定义的库
from WebModel.items import PageItem, RulesetItem
# [robots.txt解析库(进行过修改)](http://nikitathespider.com/python/rerp/)
from WebModel.utils.robotexclusionrulesparser import RobotExclusionRulesParser as RobotsParser
# [域名解析库](https://pypi.python.org/pypi/publicsuffix/)
from WebModel.utils.publicsuffix import domain_getter, TYPE_DOMAIN, TYPE_IP
# 数据库操作 
from WebModel.database.databasehelper import getCliInstance
# scrapy-redis库
from WebModel.utils.scrapy_redis.spiders import RedisMixin
# 爬虫从redis的 `url_queue_key`、`domains_key` 键中获取需要爬取的url
from WebModel.utils.rediskeys import url_queue_key, domains_key, robots_refused_key, url_ignore_key, url_visited_key

class WebModelSpider(RedisMixin, Spider):

	name = 'webmodel'
	# CRAWLING_DOMAIN = 'qq.com'
	# CRAWLING_DOMAIN = '163.com'
	# CRAWLING_DOMAIN = "people.com.cn"
	# CRAWLING_DOMAIN = "xinhuanet.com"
	# CRAWLING_DOMAIN = "cntv.cn"
	# CRAWLING_DOMAIN = "ifeng.com"
	# CRAWLING_DOMAIN = "hexun.com"
	# CRAWLING_DOMAIN = "sina.com.cn"
	# CRAWLING_DOMAIN = "sohu.com"
	# CRAWLING_DOMAIN = "dbw.cn"
	CRAWLING_DOMAIN = None

	def set_crawler(self, crawler, *args, **kwargs):
		super(WebModelSpider, self).set_crawler(crawler)
		self.setup_redis()
		if not self.server.exists(self.URL_QUEUE_KEY):
			# 初始爬取网址
			self.server.lpush(self.URL_QUEUE_KEY, self.BEGIN_URL)

		self.log("`set_crawler` Reading URLs from redis list '%s'" % self.URL_QUEUE_KEY, level=log.INFO)
	
	def __init__(self, begin="http://www.163.com"):
		super(WebModelSpider, self).__init__()
		print 'initing spider with begin:',begin
		# 根据begin参数修改redis数据库中存储键值
		self.CRAWLING_DOMAIN = domain_getter.get_domain(begin)[0]
		self.URL_QUEUE_KEY = url_queue_key%self.CRAWLING_DOMAIN
		self.URL_VISITED_KEY = url_visited_key%self.CRAWLING_DOMAIN
		self.BLOG_IGNORE_KEY = url_ignore_key%self.CRAWLING_DOMAIN
		self.ROBOT_REFUSED_KEY = robots_refused_key%self.CRAWLING_DOMAIN
		
		self.BEGIN_URL = begin

		# print self.CRAWLING_DOMAIN,self.URL_QUEUE_KEY,self.URL_VISITED_KEY,self.BLOG_IGNORE_KEY,self.ROBOT_REFUSED_KEY

		# 用来解析url获取域名
		# for url in WebModelSpider.start_urls:
		# 	import sqlite3
		# 	try:
		# 		domain = domain_getter.get_public_suffix(urlparse(url).netloc)
		# 		getCliInstance().insertWebsite(url, domain)
		# 	except sqlite3.IntegrityError:
		# 		getCliInstance().rollback()

	def parse(self, response):
		if response.status != 200:
			self.log("Response code: %d from %s"%(response.status, response['url']), level=log.WARNING)
			return
		# 解析url,获取域名
		netloc = urlparse(response.url).netloc
		domain, ret_type = domain_getter.get_domain(response.url)

		# 检查并获取domain对应的robots内容
		# robotsparser用以判断url是否被robots.txt内规则允许
		robotsparser, rulesetItem = self.getRuleset(domain)
		# 把rulesetItem送到pipeline
		yield rulesetItem

		#IP地址
		if ret_type == TYPE_IP:
			return
			
		pageItem = PageItem()
		# 使用xpath获取内容
		pageItem['url'] = response.url
		hxs = Selector(text=response.body)
		try:
			pageItem['title'] = hxs.xpath('/html/head/title/text()').extract()[0]
		except IndexError:
			pageItem['title'] = '(crwal title failed)'
		pageItem['links'] = []
		pageItem['refused_links'] = []

		# 把所有<a>标签的超链接提取出来
		for link in hxs.xpath('//a/@href').extract() :
			# 判断超链接内容是否为一个合法网址/相对网址
			if link.startswith('http://') :
				pageItem['links'].append(link)
				# robots判定
				if not robotsparser or robotsparser.is_allowed('*', link):
					pageItem['links'].append(link)

					#Schedule从redis队列中获取, 不在这里发起请求
					# yield Request(link, callback=self.parse)
				else:
					pageItem['refused_links'].append(link)

			elif link.startswith('/') :
				# 相对定位,把网址补全,再yield请求
				link = "http://"+ netloc + link
				pageItem['links'].append(link)
				# robots判定
				if not robotsparser or robotsparser.is_allowed('*', link) :
					pageItem['links'].append(link)

					#Schedule从redis队列中获取, 不在这里发起请求
					# yield Request(link, callback=self.parse)
				else:
					pageItem['refused_links'].append(link)
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
		#redis
		exist = self.server.exists(domains_key%domain)
		ruleset = self.server.hget(domains_key%domain, 'ruleset')
		#sqlite3
		# exist, ruleset = getCliInstance().robotsrulesetOfDomain(domain)
		robotsURL = "http://www."+domain+"/robots.txt"
		if not exist:
			# 从网络读取robots.txt文件
			self.log("fetching robots.txt from "+robotsURL, level=log.INFO)
			if robotsparser.fetch(robotsURL, timeout=5):
				ruleset = str(robotsparser)
				self.log("Successfully parse "+robotsURL, level=log.INFO)
			else:
				ruleset = '(nil)'
				self.log("robots.txt NOT found.")
			# 标记让pipeline更新数据库内容
			rulesetItem['update'] = True
		else :
			if not ruleset:
				# 重新解析robots.txt
				if robotsparser.fetch(robotsURL, timeout=5):
					ruleset = str(robotsparser)
					self.log("Successfully parse "+robotsURL, level=log.INFO)
				else:
					ruleset = '(nil)'
					self.log("robots.txt NOT found.")
				rulesetItem['update'] = True
			elif ruleset != '(nil)':
				self.log("resume robots.txt of %s from database."%(domain), level=log.INFO)
				robotsparser.parse(ruleset)
				rulesetItem['update'] = False
			else:
				robotsparser = None
				rulesetItem['update'] = True
			# 标记让pipeline不处理这个item

		rulesetItem['domain'] = domain
		rulesetItem['ruleset'] = ruleset

		return (robotsparser, rulesetItem)
