#!/usr/bin/python
#encoding:utf-8

from publicsuffix import PublicSuffixList

domainParser = PublicSuffixList()
# print domainParser.get_public_suffix("www.example.com.cn")
# print domainParser.get_public_suffix("www.example.com.uk")
# print domainParser.get_public_suffix("jaysonhwang.sinaapp.com")
# print domainParser.get_public_suffix("1.jaysonhwang.sinaapp.com")
# print domainParser.get_public_suffix("jaysonhwang.sinaapp.com/web/1")

print domainParser.get_domain("http://192.168.0.100:8080/web")
print domainParser.get_domain("http://jaysonhwang.com")
allow = [
    "http://www.people.com.cn",
    "http://www.xinhuanet.com",
    "http://www.qq.com",
    "http://www.163.com",
    "http://www.cntv.cn",
    "http://www.ifeng.com",
    "http://www.hexun.com",
    "http://www.sina.com.cn",
    "http://www.sohu.com",
    "http://www.dbw.cn",]
for a in allow:
    print domainParser.get_domain(a)[0]
