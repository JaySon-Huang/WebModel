WebModel
========

## 背景与需求
全球万维网呈现如下的结构：Web的结构  
自从参考文献[1]中2002年，北京大学利用天网搜索引擎进行连续4次大规模搜集记录，揭示了中国2002年初中国Web的大小、形状和结构。文献[1]指出，2002年初中国大约有5000万网页和5万个Web站点，而根据参考文献[2]中统计，截至2014年6月，中国网站数量为273万个。近十多年来，中国互联网得到了快速发展，近期更是兴起了移动互联网的浪潮。而中国Web的大小、形状和结构在互联网发展浪潮中是否发生改变，近年来相关的研究缺乏。

## 目的任务
学习并设计一个网页爬虫，抓取中国网页。对抓取到的网页进行去重，记录并分析去重方法的效果；分析抓取到的网页的统计值：如多少出度、入度，中国web的大小、形状等信息。

## 设计内容
1. 基本功能
	1. 设计一个爬虫，并能根据网站robots.txt避开网站不想被抓取的网页；  
	2. 设计一个合理可行的起始地址池；
	3. 设计一种去重方法进行去重，记录去重方法的相关数据；
	4. 分析抓取到的网页的统计信息，数量、平均出度、平均入度等；
	5. 通过抓取的网页信息分析中国web的大小和形状；
	6. 设计GUI界面展示效果。
2. 额外分析
	1. 尝试统计你抓到的作弊网页的数量和占比；
	2. 被拒绝抓取的网站URL、数量和占比。
	3. 尝试使用分布式爬取(利用小组成员的机器形成小集群)

### 
#### 起始地址池
[中国门户网站排行榜(2014-12-5)](http://top.chinaz.com/list.aspx?t=247)

* [人民网](www.people.com.cn)
* [新华网](www.xinhuanet.com)
* [腾讯网](www.qq.com)
* [网易](www.163.com)
* [央视网](www.cntv.cn)
* [凤凰网](www.ifeng.com)
* [和讯网](www.hexun.com)
* [新浪网](www.sina.com.cn)
* [搜狐](www.sohu.com)
* [东北网](www.dbw.cn)

## 环境
* [Python 2.7.x](python.org)  
* [Scrapy - 网络爬虫框架](scrapy.org)  
* Scrapy依赖库: [Twisted, six, w3lib, queuelib, lxml, pyOpenSSL, cssselect ]  
* Twisted依赖库: [zope.interface]  
* [pybloom - bloom filter的python实现](https://github.com/jaybaird/python-bloomfilter/)  
* pybloom依赖库: [bitarray](https://pypi.python.org/pypi/bitarray/)  
* [publicsuffix - 获取域名](https://pypi.python.org/pypi/publicsuffix/)  
* [robotexclusionrulesparser - 解析robots.txt](http://nikitathespider.com/python/rerp/)  
* [Redis - 作为分布式队列](http://www.redis.io/)  
* Scrapy 和 Redis 的融合: [scrapy-redis](https://github.com/darkrho/scrapy-redis)(对新版的Scrapy适配做了调整)  
* python操作Redis数据库: [redis-py](https://github.com/andymccurdy/redis-py)  

## 参考文献
1. 闫宏飞，李晓明，关于中国Web 的大小、形状和结构，计算机研究和发展，2002，39（8）：958~967
2. 中国互联网络信息中心（CNNIC）[第34次中国互联网络发展状况统计报告](url:http://www.cnnic.net.cn/hlwfzyj/hlwxzbg/hlwtjbg/201407/P020140721507223212132.pdf)，2014年07月21日，
