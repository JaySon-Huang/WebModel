# -*- coding: utf-8 -*-
from scrapy import log

# _REDIS_URLQUEUE_KEY = '%(spider)s:urls_to_visit'
# # Redis中存储的Key, 类型为 Set
# _REDIS_DOMAINS_KEY = '%(spider)s:domains'
# # Redis中存储的Key, 类型为 哈希表
# _REDIS_RULESETS_KEY = '%(spider)s:rulesets'

url_queue_key = 'webmodel:%s:urls_to_visit'
# 集合
url_visited_key = 'webmodel:%s:urls_visited'
# 集合
url_ignore_key = 'webmodel:%s:urls_ignore'
robots_refused_key = 'webmodel:%s:refused'
related_domains_key = 'webmodel:%s:domains:%s'

domains_key = 'webmodel:domains:%s'


# url_queue_key = 'tmp:urls_to_visit'
# url_visited_key = 'tmp:urls_visited'
# url_ignore_key = 'tmp:urls_ignore'
# domains_key = 'tmp:domains:%s'

# def load(spider):
#     global url_queue_key,domains_key
#     url_queue_key = _REDIS_URLQUEUE_KEY%{'spider':spider.name}
#     domains_key = _REDIS_DOMAINS_KEY%{'spider':spider.name}
#     spider.log('Using Redis Key:%s|%s'%(url_queue_key, domains_key), level=log.INFO)
