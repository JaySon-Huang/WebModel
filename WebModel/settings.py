# -*- coding: utf-8 -*-

# Scrapy settings for WebModel project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'WebModel'

SPIDER_MODULES = ['WebModel.spiders']
NEWSPIDER_MODULE = 'WebModel.spiders'
ITEM_PIPELINES = {
	'WebModel.pipelines.WebModelPipeline': 200,
}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'WebModel (+http://www.yourdomain.com)'

# # Enables scheduling storing requests queue in redis.
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# # Don't cleanup redis queues, allows to pause/resume crawls.
# SCHEDULER_PERSIST = True

# # Schedule requests using a priority queue. (default)
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# # Schedule requests using a queue (FIFO).
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'

# # Schedule requests using a stack (LIFO).
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderStack'

# # Max idle time to prevent the spider from being closed when distributed crawling.
# # This only works if queue class is SpiderQueue or SpiderStack,
# # and may also block the same time when your spider start at the first time (because the queue is empty).
# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# # Store scraped item in redis for post-processing.
# ITEM_PIPELINES = [
#     'scrapy_redis.pipelines.RedisPipeline',
# ]

# # Specify the host and port to use when connecting to Redis (optional).
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
