# -*- coding: utf-8 -*-
import requests
import re

class RobotsHandler(object):

	regex_useragent = re.compile(r'User-agent:(.+)$')
	# regex_allow = re.compile(r'Allow:(.+)$')
	regex_disallow = re.compile(r'Disallow:(.+)$')

	def __init__(self, domain):
		self.domain = domain
		self.disallows = []
		self.parseTXT()

	def parseTXT(self):
		# 不允许自动跳转
		r = requests.get(self.domain+'/robots.txt', allow_redirects=False)
		# 状态号非200表示获取失败,没有robots.txt文件
		if r.status_code != 200:
			return

		cur_ua = None
		disallows = []
		for line in r.text.split('\n'):

			extract = RobotsHandler.regex_useragent.match(line)
			if extract :
				cur_ua = extract.group(1).strip()
				continue

			extract = RobotsHandler.regex_disallow.match(line)
			if extract and cur_ua == '*':
				disallow = extract.group(1).strip()
				disallows.append(disallow)
				# print 'New disallow rule:',disallow
				continue
		print disallows
		
		for rule in disallows :
			rule = rule.replace('.','\.').replace('*','.*').replace('?','\?')
			rule = rule.replace('+','\+').replace('{','\{').replace('}','\}')
			rule = rule.replace('(','\(').replace(')','\)').replace('[','\[').replace(']','\]')
			# self.disallows.append( re.compile(rule, flags=re.DEBUG) )
			self.disallows.append( re.compile(rule) )

	def filter(self, links, META=None):
		'''
		根据self.domain域名根目录下robots.txt定义的规则,对url列表进行过滤

		@links url列表
		@META  为抓取单个网页的robots META标签留空位
		@return 以字典形式返回.
		        'allows'为links中允许的url列表
		        'disallows'中每一项为links中被规则过滤的url,与过滤此url的规则
		'''
		ret = {
			'allows':[],
			'disallows':[],
		}
		# 域名下没有robots.txt禁止的内容
		if not self.disallows:
			ret['allows'] = links
			return ret

		# 有robots.txt禁止的内容,对url进行过滤
		for link in links :
			isAllow = True
			for rule in self.disallows :
				m = rule.match(link)
				if m : # 其中一条robots规则符合此条url
					isAllow = False
					ret['disallows'].append((link, rule.pattern))
					break
			if isAllow :
				ret['allows'].append(link)
		return ret

r = RobotsHandler('http://zhihu.com')
print r.filter(['/login/?uid=123'])
