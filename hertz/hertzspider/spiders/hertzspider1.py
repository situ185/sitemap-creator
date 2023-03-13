import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_playwright.page import PageMethod
import traceback
import os
from scrapy.linkextractors import LinkExtractor
import logging
# from urllib import robotparser
from scrapy.exceptions import IgnoreRequest

from twisted.internet.error import DNSLookupError, TCPTimedOutError
from playwright.sync_api import Playwright, sync_playwright
from playwright._impl._api_types import TimeoutError
from twisted.python.failure import Failure

try:
    os.remove('../hertz/hertzspider/new_new_outputs/output.xml')
    os.remove('../hertz/hertzspider/new_new_outputs/log.log')
except OSError:
    pass

logging.basicConfig(filename='../hertz/hertzspider/new_new_outputs/log.log', level=logging.DEBUG)
logging.getLogger('scrapy').setLevel(logging.WARNING)
logging.getLogger('playwright').setLevel(logging.WARNING)


# def set_playwright_true(request, response):
#     request.meta["playwright"] = True
#     request.meta["playwright_include_page"] = True,
#     request.meta["playwright_page_methods"] = [PageMethod('wait_for_selector', 'div#container')]
#     return request


class HertzspiderSpider(scrapy.Spider):
    name = 'hertzspider'
    # allowed_domains = ['hertz.com']

    custom_settings = {
        'FEEDS': {'../hertz/hertzspider/new_new_outputs/output.xml': {"format": 'xml'}},
        "LOG_LEVEL": "INFO",
    }

    # headers = {
    #            'user-agent' : "hertz-sitemap-builder"
    # }

    # when the class is 1st instantiated
    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        self.link_extractor = LinkExtractor(canonicalize=True, unique=True,
                                            allow_domains=[self.domain],
                                            deny=['/p/', '/A-thou-doe-prospeeceiud-accome-Hauen-heeleepell'],
                                            deny_domains=['salesforceliveagent.com', 'google-analytics.com',
                                                          'analytics.google.com',
                                                          'c.clicktale.net']
                                            )
        self.links = []
        self.error_urls = []
        self.failure = {}
        logger = logging.getLogger(__file__)

        # self.robot_parser = robotparser.RobotFileParser()
        # self.robot_parser.set_url(f'https://{self.domain}/robots.txt')
        # self.robot_parser.read()



    def start_requests(self):
        yield scrapy.Request(f'https://{self.domain}/rentacar/reservation',
                             # headers={"User-Agent": "hertz-sitemap-builder"},
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 playwright_page_methods=[
                                     PageMethod('wait_for_selector', 'div#container'),
                                     PageMethod("wait_for_timeout", float(10000))
                                 ],
                                 errback=self.errback,
                             )
                             )

    async def parse(self, response):
        """ build the initial list off the input domain """
        page = response.meta["playwright_page"]
        await page.close()

        links_object = self.link_extractor.extract_links(response)
        # links_object = response.css("a::attr('href')")
        self.logger.info("{0} {1} {2} ".format('Links', 'in', 'domain') + response.url + "{}".format(':'))
        self.logger.info(links_object)
        self.logger.info("=" * 30)
        for link in links_object:
            try:

                link_to_follow = link.url
                # link_to_follow = link.get()
                # yield {
                #    "loc" : link.url
                # }

                yield scrapy.Request(link_to_follow,
                                     #headers={"User-Agent": "hertz-sitemap-builder"},
                                     callback=self.parseUrl,
                                     errback=self.parseError,
                                     cb_kwargs=dict(request_link=link_to_follow, retry=False),
                                     meta=dict(
                                         playwright=True,
                                         playwright_include_page=True,
                                         playwright_page_methods=[
                                             PageMethod('wait_for_selector', 'div#container'),
                                             PageMethod("wait_for_timeout", 10000)
                                         ]
                                     )
                                     )
            except Exception as E:
                self.logger.error(traceback.format_exc())
                self.logger.error(repr(E))
                yield {
                    'error': "error fetching " + link.get(),
                    'status': response.status
                }

    async def parseUrl(self, response, request_link, retry):
        if not retry:
            page = response.meta["playwright_page"]
            await page.close()
        else:
            pass

        try:
            self.logger.info(retry)
            self.logger.info("*" * 50)
            self.logger.info("visited  %s", response.url)
            self.logger.info("request_link is %s", request_link)
            self.logger.info("status for rl-{0} ru-{1} {2} ".format(request_link, response.url, response.status))
            self.logger.info("*" * 50)
            if response.status == 200:
                if response.url not in self.links:
                    self.links.append(response.url)
                    yield {
                        'loc': response.url
                    }

                try:
                    self.logger.info("closing " + response.url)
                    await page.close()
                except Exception as e:
                    self.logger.error(f"Failed to close browser context: {str(e)}")
                finally:
                    await page.close()

        except Exception as E:
            self.logger.error('exception')
            self.logger.error(repr(E))
            yield {
                'loc': "error"
            }

        # url_item=HertzItem()
        # try:
        #     if response.status == 200:
        #         url_item=HertzURLLoader(item=HertzItem(), response=response)
        #         url_item.add_value('loc','request_link')
        #         yield url_item.load_item()

        #     else:
        #         yield{
        #             'loc':"error"
        #         }
        # except:
        #     yield{
        #         'loc':"error"
        #     }

    async def retryLogicc(self):
        self.logger.error('retrying')
        links_object = self.error_urls
        # links_object = response.css("a::attr('href')")
        self.logger.info("{0} {1} {2} ".format('Links', 'in', 'error_urls') + "{}".format(':'))
        self.logger.info(links_object)
        self.logger.info("~" * 30)
        for link in links_object:
            try:

                link_to_follow = link.url
                # link_to_follow = link.get()
                # yield {
                #    "loc" : link.url
                # }

                yield scrapy.Request(link_to_follow,
                                     # headers={"User-Agent": "hertz-sitemap-builder"},
                                     callback=self.parseUrl,
                                     errback=self.parseError,
                                     cb_kwargs=dict(request_link=link_to_follow, retry=True),
                                     meta=dict(
                                         playwright=True,
                                         playwright_context="error_pages",
                                         playwright_include_page=False,
                                         # playwright_page_methods=[
                                         #     PageMethod('wait_for_selector', 'div#container'),
                                         #     PageMethod("wait_for_timeout", 10000)
                                         # ]
                                     )
                                     )
            except Exception as E:
                print(traceback.format_exc())
                self.logger.error(repr(Exception))
                # yield {
                #     'error': "error fetching " + link.get(),
                #     'status': response.status
                # }
    async def parseError(self, failure):
        page = failure.request.meta["playwright_page"]

        self.failure = failure
        self.logger.error("Inside parseError")
        self.logger.error(repr(failure))
        self.logger.info("failure in  %s", failure.request.cb_kwargs['request_link'])
        self.logger.error(traceback.format_exc())
        # yield {
        #     'failure_url': failure.request.cb_kwargs['request_link'],
        #     'status': failure.status
        # }

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpErrorr on %s', response.url)
            self.error_urls.append(response.url)
            # self.retryLogic(self.failure)
            self.retryLogicc()

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupErrorr on %s', request.url)
            self.error_urls.append(request.url)
            # self.retryLogic(self.failure)
            self.retryLogicc()

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutErrorr on %s', request.url)
            self.error_urls.append(request.url)
            self.retryLogicc()



        # link_to_follow = failure.request.url
        #
        # self.logger.error('retrying on %s', link_to_follow)
        #
        # yield scrapy.Request(link_to_follow,
        #                      # headers={"User-Agent": "hertz-sitemap-builder"},
        #                      callback=self.parseUrl,
        #                      errback=self.parseError,
        #                      cb_kwargs=dict(request_link=link_to_follow, retry=True),
        #                      meta=dict(
        #                          playwright=True,
        #                          playwright_include_page=False,
        #                          # playwright_page_methods=[
        #                          #     PageMethod('wait_for_selector', 'div#container'),
        #                          #     PageMethod("wait_for_timeout", 10000)
        #                          # ]
        #                      )
        #                      )

    async def errback(self, failure):
        self.logger.error("Inside errBack")
        # self.retryLogicc()

        page = failure.request.meta["playwright_page"]
        await page.close()

    def testMe(self):
        self.logger.error('retrying')
        failure = self.failure
        # page = failure.request.meta["playwright_page"]

        link_to_follow = failure.request.url

        self.logger.error('retrying on %s', link_to_follow)

        yield scrapy.Request(link_to_follow,
                             # headers={"User-Agent": "hertz-sitemap-builder"},
                             callback=self.parseUrl,
                             errback=self.parseError,
                             cb_kwargs=dict(request_link=link_to_follow),
                             )
