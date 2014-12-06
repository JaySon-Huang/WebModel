from scrapy import log

from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider

import WebModel.utils.scrapy_redis.connection as connection
from WebModel.utils.rediskeys import url_queue_key

class RedisMixin(object):
    """Mixin class to implement reading urls from a redis queue."""
    # redis_key = None  # use default '<spider>:start_urls'

    def setup_redis(self):
        """Setup redis connection and idle signal.

        This should be called after the spider has set its crawler object.
        """
        # if not self.redis_key:
            # self.redis_key = '%s:start_urls' % self.name
        self.server = connection.from_settings(self.crawler.settings)
        # idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        self.crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        self.crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)

    def next_request(self):
        """Returns a request to be scheduled or none."""
        url = self.server.lpop(url_queue_key)
        if url:
            return self.make_requests_from_url(url)

    def schedule_next_request(self):
        """Schedules a request if available"""
        req = self.next_request()
        if req:
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        self.schedule_next_request()
        raise DontCloseSpider

    def item_scraped(self, *args, **kwargs):
        """Avoids waiting for the spider to  idle before scheduling the next request"""
        self.schedule_next_request()


class RedisSpider(RedisMixin, Spider):
    """Spider that reads urls from redis queue when idle."""

    def set_crawler(self, crawler):
        # super(RedisSpider, self).set_crawler(crawler)
        self.setup_redis()
        self.log("`set_crawler` Reading URLs from redis list '%s'" % url_queue_key, level=log.INFO)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        try:
            spider = super(RedisSpider, cls).from_crawler(crawler, *args, **kwargs)
        except AttributeError:
            spider = cls()
            super(RedisSpider ,spider).set_crawler(crawler)
        spider.setup_redis()
        # load(spider)
        spider.log("`from_crawler` Reading URLs from redis list '%s'" % url_queue_key, level=log.INFO)
        return spider

