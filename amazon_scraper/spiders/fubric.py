import scrapy


class FubricSpider(scrapy.Spider):
    name = "fubric"
    allowed_domains = ["www.amazon.com"]
    start_urls = ["http://www.amazon.com/"]

    def parse(self, response):
        pass
