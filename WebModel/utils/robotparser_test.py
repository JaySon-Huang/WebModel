#!/usr/bin/python
#encoding:utf-8

from robotexclusionrulesparser import RobotExclusionRulesParser as RobotsParser

rb = RobotsParser()
# rb.fetch("http://www.zhihu.com/robots.txt")
# print rb
# print rb._RobotExclusionRulesParser__rulesets
# print rb.is_allowed('*', 'http://www.zhihu.com/loginasdkj?encode=12')
# print rb.is_allowed('*', '/admin_inbox')
# print '======'

rb.fetch("http://www.iplaypython.com/robots.txt")
print rb
print '======'

rb.fetch("http://baidu.com/robots.txt")
print rb
print '======'

rb.fetch("http://jaysonhwang.com/robots.txt")
print rb
print '======'
