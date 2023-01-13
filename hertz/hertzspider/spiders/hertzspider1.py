import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_playwright.page import PageMethod
import traceback
import os
from scrapy.linkextractors import LinkExtractor
import logging

from twisted.internet.error import DNSLookupError, TCPTimedOutError

logging.basicConfig(level=logging.CRITICAL, filename="../hertz/hertzspider/outputs/log3.log")


def set_playwright_true(request, response):
    request.meta["playwright"] = True
    request.meta["playwright_include_page"] = True,
    request.meta["playwright_page_methods"] = [PageMethod('wait_for_selector', 'div#container')]
    return request


class HertzspiderSpider(scrapy.Spider):
    name = 'hertzspider1'
    allowed_domains = ['hertz.com']

    try:
        os.remove('../output.xml')
    except OSError:
        pass

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        self.link_extractor = LinkExtractor(unique=True)
        self.links = []
        logger = logging.getLogger(__file__)

    def start_requests(self):
        yield scrapy.Request(f'https://{self.domain}/rentacar/reservation',
                             headers={"User-Agent": "hertz-sitemap-builder"},
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

        links = list()
        links_object = self.link_extractor.extract_links(response)
        self.logger.info("links in page  " + response.url + ":")
        self.logger.info(links_object)
        for link in links_object:

            self.logger.info("appending %s to list.", link.url)
            links.append(link.url)
            try:

                time.sleep(2)

                link_to_follow = link.url
                # yield {
                #    "loc" : link.url
                # }
                if link not in self.links:

                    yield scrapy.Request(link_to_follow,
                                         headers={"User-Agent": "hertz-sitemap-builder"},
                                         callback=self.parseUrl,
                                         errback=self.parseError,
                                         cb_kwargs=dict(request_link=link_to_follow),
                                         meta=dict(
                                             playwright=True,
                                             playwright_include_page=True,
                                             playwright_page_methods=[
                                                 PageMethod('wait_for_selector', 'div#container'),
                                                 PageMethod("wait_for_timeout", 10000)
                                             ]
                                         )
                                         )
            except Exception:
                print(traceback.format_exc())
                self.logger.error(repr(Exception))
                yield {
                    'error': "error fetching " + link.get(),
                    'status': response.status
                }

    async def parseUrl(self, response, request_link):
        page = response.meta["playwright_page"]
        await page.close()

        try:
            self.logger.info("following  %s", response.url)
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
        self.logger.info("failure in  %s", failure.request.cb_kwargs['request_link'])
        # yield {
        #     'failure_url': failure.request.cb_kwargs['request_link'],
        #     'status': failure.status
        # }

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
