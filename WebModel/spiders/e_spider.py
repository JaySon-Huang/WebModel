from scrapy.spider import Spider

class MySpider(Spider):
    name = 'myspider'

    def __init__(self, first=None):
        print 'initing with first:',first

    def parse(self, response):
		print response.status
		pass
