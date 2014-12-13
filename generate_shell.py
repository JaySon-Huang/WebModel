# -*- coding: utf-8 -*-
websites = {
    'people':"http://www.people.com.cn",
    'xinhuanet':"http://www.xinhuanet.com",
    'qq'    :"http://www.qq.com",
    '163'   :"http://www.163.com",
    'cntv'  :"http://www.cntv.cn",
    'ifeng' :"http://www.ifeng.com",
    'hexun' :"http://www.hexun.com",
    'sina'  :"http://www.sina.com.cn",
    'sohu'  :"http://www.sohu.com",
    'dbw'   :"http://www.dbw.cn",
}
for name,website in websites.iteritems():
    with open("crawl_%s.sh"%name,'w') as of:
        line = "scrapy crawl webmodel --logfile=./crawl_%s.log -L INFO -a begin='%s'"%(name,website)
        of.write(line)
