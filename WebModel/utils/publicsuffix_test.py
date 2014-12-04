#!/usr/bin/python
#encoding:utf-8

from publicsuffix import PublicSuffixList

domainParser = PublicSuffixList()
print domainParser.get_public_suffix("www.example.com.cn")
print domainParser.get_public_suffix("www.example.com.uk")
print domainParser.get_public_suffix("jaysonhwang.sinaapp.com")
print domainParser.get_public_suffix("1.jaysonhwang.sinaapp.com")
print domainParser.get_public_suffix("jaysonhwang.sinaapp.com/web/1")

