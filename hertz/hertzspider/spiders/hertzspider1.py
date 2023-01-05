import scrapy
from scrapy_playwright.page import PageMethod
import traceback
import os
from scrapy.linkextractors import LinkExtractor
import logging


def set_playwright_true(request, response):
    request.meta["playwright"] = True
    request.meta["playwright_include_page"] = True,
    request.meta["playwright_page_methods"] = [PageMethod('wait_for_selector', 'div#container')]
    return request


class HertzspiderSpider(scrapy.Spider):
    name = 'hertzspider1'
    allowed_domains = ['hertz.com']

    try:
        os.remove('output.xml')
    except OSError:
        pass

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        self.link_extractor = LinkExtractor(unique=True)
        self.links = []

    def start_requests(self):
        yield scrapy.Request(f'https://{self.domain}/rentacar/reservation',
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 errback=self.errback,
                                 playwright_page_methods=[
                                     PageMethod('wait_for_selector', 'div#container'),
                                     PageMethod("wait_for_timeout", float(10000))
                                 ]
                             )
                             )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        links = self.link_extractor.extract_links(response)

        for link in links:
            try:
                self.logger.info("Visiting %s", link.url)

                link_to_follow = link.url
                # yield {
                #    "loc" : link.url
                # }
                if link not in self.links:
                    yield response.follow(link_to_follow,
                                          callback=self.parseURL,
                                          errback=self.parseError,
                                          cb_kwargs=dict(request_link=link_to_follow),
                                          meta=dict(
                                              playwright=True,
                                              playwright_include_page=True,
                                              playwright_page_methods=[
                                                  PageMethod('wait_for_selector', 'div#container'),
                                                  PageMethod("wait_for_timeout", 10000)
                                              ],
                                              request_link=link_to_follow
                                          )
                                          )
            except Exception:
                print(traceback.format_exc())
                self.logger.error(repr(Exception))
                yield {
                    'error': "error fetching " + link.get(),
                    'status': response.status
                }

    async def parseURL(self, response, request_link):
        try:
            self.logger.info("response is  %s", response.url)
            self.logger.info("request_link is %s", request_link)
            if response.status == 200:
                yield {
                    'loc': response.url
                }

        except Exception:
            yield {
                'loc': "error"
            }

    async def parseError(self, failure):
        yield {
            'failure_url': failure.url,
            'status': failure.status
        }

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
