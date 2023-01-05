import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_playwright.page import PageMethod
from array import array


def set_playwright_true(request, response):
    request.meta["playwright"] = True
    request.meta["playwright_include_page"] = True,
    request.meta["playwright_page_methods"] = [PageMethod('wait_for_selector', 'div#container')]
    return request


class HertzSitemapCrawlerSpider(CrawlSpider):
    name = 'hertz_sitemap_crawler'
    allowed_domains = ['hertz.com']

    def start_requests(self):
        yield scrapy.Request('https://www.hertz.com/rentacar/reservation',
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 errback=self.errback,
                                 playwright_page_methods=[
                                     PageMethod('wait_for_selector', 'div#container')
                                 ]
                             )
                             )

    rules = (
        Rule(LinkExtractor(allow_domains=('www.hertz.com',), unique=True), callback='parse_item', follow=True,
             process_request=set_playwright_true),
    )

    async def parse_item(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        print("crawling " + response.url)
        yield {
            'loc': response.url
        }
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
