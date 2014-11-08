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
		r = requests.get(self.domain+'/robots.txt')
		cur_ua = None
		disallows = []
		for line in r.text.split('\n'):

			extract = RobotsHandler.regex_useragent.match(line)
			if extract :
				cur_ua = extract.group(1).strip()
				# print 'Current User-agent:',cur_ua
				continue

			# extract = RobotsHandler.regex_allow.match(line)
			# if extract and cur_ua == '*':
			# 	allow = extract.group(1).strip()
			# 	self.rules['allow'].append(allow)
			# 	print 'New allow rule:',allow
			# 	continue

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
		@return 以字典形式返回.
		        'allows'为links中允许的url列表
		        'disallows'中每一项为links中被规则过滤的url,与过滤此url的规则
		'''
		ret = {
			'allows':[],
			'disallows':[],
		}
		for link in links :
			isAllow = True
			for rule in self.disallows :
				m = rule.match(link)
				if m : # 其中一条robots规则禁止此条url的抓取
					isAllow = False
					ret['disallows'].append((link, rule.pattern))
					break
			if isAllow :
				ret['allows'].append(link)
		return ret

r = RobotsHandler('http://zhihu.com')
print r.filter(['/login/?uid=123'])
