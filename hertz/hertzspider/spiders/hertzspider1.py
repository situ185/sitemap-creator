import json
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
from scrapy.shell import inspect_response

try:
    os.remove('../outputs/output17.xml')
    os.remove('../outputs/log17.log')
except OSError:
    pass

logging.basicConfig(filename='../outputs/log17.log', level=logging.INFO)
logging.getLogger('scrapy').setLevel(logging.ERROR)
logging.getLogger('playwright').setLevel(logging.ERROR)


# def set_playwright_true(request, response):
#     request.meta["playwright"] = True
#     request.meta["playwright_include_page"] = True,
#     request.meta["playwright_page_methods"] = [PageMethod('wait_for_selector', 'div#container')]
#     return request

def should_abort_requests(request):
    """ do not download these resources """
    if request.resource_type == 'image':
        return True
    elif request.resource_type == 'stylesheet':
        return True
    elif request.resource_type == 'media':
        return True
    elif request.resource_type == 'font':
        return True
    # elif request.resource_type == 'xhr':
    #     return True

    return False


class HertzspiderSpider(scrapy.Spider):
    name = 'hertzspider'
    handle_httpstatus_list = [500]

    custom_settings = {
        'FEEDS': {'../outputs/output17.xml': {"format": 'xml'}},
        "LOG_LEVEL": "ERROR",
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_requests
    }

    headers = {
    #             'x-irac-bot-access': "true"
        'User-Agent': "hertz-sitemap-builder",
        'x-irac-bot-access': 'true'
    }

    def __init__(self, name=None, **kwargs):
        """when the class is 1st instantiated"""
        super().__init__(name, **kwargs)

        self.link_extractor = LinkExtractor(canonicalize=False, unique=True,
                                            allow_domains=[self.domain],
                                            deny=['/p/', '/location','/drivingforward','/rest/',
                                                  '/A-thou-doe-prospeeceiud-accome-Hauen-heeleepell'],
                                            deny_domains=['pub.emails.hertz.com', 'salesforceliveagent.com', 'google-analytics.com',
                                                          'analytics.google.com',
                                                          'c.clicktale.net'],
                                            )
        self.links = []  # list that holds URLs that come back with a 200, so that they dont get crawled in a loop
        self.error_urls = []  # temporary list to hold URLs that cannot be scraped with playwright
        self.error_400_urls = []  # temporary list to hold URLs that cannot be scraped with playwright
        self.error_DNS_urls = []  # temporary list to hold URLs that cannot be scraped with playwright
        self.following_links = []  # URLs that are already being followed, do not follow URLs that are already in the queue/this list
        self.error_500_urls = []
        logger = logging.getLogger(__file__)

        # self.robot_parser = robotparser.RobotFileParser()
        # self.robot_parser.set_url(f'https://{self.domain}/robots.txt')
        # self.robot_parser.read()

    def start_requests(self):
        """ start program here """
        self.logger.info("Starting program for %s", f'https://{self.domain}')

        # yield an initial one time request to the domain homepage
        yield scrapy.Request(f'https://{self.domain}/rentacar/reservation',
                             dont_filter=True,
                             headers={'x-irac-bot-access': 'true',
                                      'User-Agent': "hertz-sitemap-builder", },
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 playwright_page_methods=[
                                     PageMethod('wait_for_selector', 'div#container'),
                                     PageMethod("wait_for_timeout", float(100000))
                                 ],
                                 errback=self.errback,
                             )
                             )

    async def parse(self, response):
        """ parse the response and build the list of links inside the page
            -recursive """

        page = response.meta["playwright_page"]
        await page.close()

        if response.status == 500:
            self.logger.error('500 on %s', response.url)
            self.logger.error(f'Adding {response.url} to error_500_urls')
            self.error_500_urls.append({response.url, response.status})
        else:

            if response.url not in self.links:  # check to see if the url is in self.links so that we dont re-crawl the page
                self.links.append(response.url)  # add the url to self.links so that we dont re-crawl the page
                self.logger.info("(Parse)Adding %s to self.links", response.url)

                canonicalURLText = response.xpath('//link[@rel="canonical"]/@href').extract()
                canonicalURL = json.dumps(canonicalURLText[0]).replace(" ", "")
                responseURL = json.dumps(response.url).replace(" ", "")
                self.logger.info("(Parse)canonicalURLText is %s,responseURL is %s", canonicalURL, responseURL)

                if canonicalURL.lower().strip() == responseURL.lower().strip():
                    yield {
                        'loc': response.url  # yield a successful page
                    }

            links_object = self.link_extractor.extract_links(response)  # extract links from current page

            # start log links from current page
            self.logger.info("{0} {1} {2} ".format('(Parse)Links', 'in', 'page') + response.url + "{}".format(':'))
            for obj in links_object:
                self.logger.info(str(obj.url))
            self.logger.info("=" * 30)
            # end log links from current page

            for link in links_object:
                try:

                    link_to_follow = link.url

                    if link_to_follow not in self.links and link_to_follow not in self.following_links:  # the URL should not already have been crawled or being followed through other crawls in process

                        self.logger.info("(Parse)started following %s", link_to_follow)
                        self.following_links.append(link_to_follow)  # this URL is in process of being crawled

                        # yield request to link_to_follow
                        yield scrapy.Request(link_to_follow,
                                             dont_filter=True,
                                             headers={'x-irac-bot-access': 'true',
                                                      'User-Agent': "hertz-sitemap-builder",},
                                             callback=self.parseUrl,
                                             errback=self.parseError,
                                             cb_kwargs=dict(request_link=link_to_follow),
                                             meta=dict(
                                                 playwright=True,
                                                 playwright_include_page=True,
                                                 playwright_page_methods=[
                                                     PageMethod('wait_for_selector', 'div#container'),
                                                     PageMethod("wait_for_timeout", 100000)
                                                 ]
                                             )
                                             )
                except Exception as E:
                    self.logger.error(traceback.format_exc())
                    self.logger.error(repr(E))
                    # no link.url exception?
                    # need better error handling

    async def parseUrl(self, response, request_link):
        """ parse the response from parse method then recursively call parse method to further extract links"""

        self.logger.info("(parseUrl)closing %s", response.url)
        page = response.meta["playwright_page"]
        await page.close()

        try:
            self.logger.info("Inside parseUrl")
            self.logger.info("*" * 50)
            self.logger.info(
                "following {0}, visited {1},status={2} ".format(request_link, response.url, response.status))
            self.logger.info("*" * 50)
            if response.status == 200:
                link_to_follow = response.url
                yield scrapy.Request(link_to_follow,
                                     dont_filter=True,
                                     headers={'x-irac-bot-access': 'true',
                                              'User-Agent': "hertz-sitemap-builder", },
                                     callback=self.parse,
                                     errback=self.parseError,
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
            self.logger.error('exception')
            self.logger.error(repr(E))
            # no response.url exception?
            # need better error handling

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

    async def parseErrorUrl(self, response, request_link):
        """ parse the response from parseError method """

        try:
            self.logger.info("retrying inside parseErrorUrl")
            self.logger.info("*" * 50)
            self.logger.info("(parseErrorUr) following {0}, visited {1},status={2} ".format(request_link, response.url,
                                                                                            response.status))
            self.logger.info("*" * 50)
            if response.status == 200:
                if response.url not in self.links:
                    self.links.append(response.url)
                    yield {
                        'loc': response.url
                    }

                # try:
                #     self.logger.info("closing " + response.url)
                #     await page.close()
                # except Exception as e:
                #     self.logger.error(f"Failed to close browser context: {str(e)}")
                # finally:
                #     await page.close()

        except Exception as E:
            self.logger.error('exception')
            self.logger.error(repr(E))

    async def retryPlaywrightRequest(self, failure):
        self.logger.error('retrying {0} since it needs playwright'.format(failure.request.url))
        yield scrapy.Request(failure.request.url,
                             dont_filter=True,
                             headers={'x-irac-bot-access': 'true',
                                      'User-Agent': "hertz-sitemap-builder", },
                             callback=self.parse,
                             errback=self.parseError,
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 playwright_page_methods=[
                                     PageMethod('wait_for_selector', 'div#container'),
                                     PageMethod("wait_for_timeout", 10000)
                                 ]
                             )
                             )

    async def parseError(self, failure):
        """ parse the errors from itself,parseUrl and parse methods """
        self.logger.info("(parseError)closing " + failure.request.url)

        page = failure.request.meta["playwright_page"]
        await page.close()

        self.logger.info("~" * 30)
        self.logger.info("Inside parseError")
        self.logger.error(repr(failure))
        self.logger.info("failure in %s", failure.request.url)
        self.logger.error(traceback.format_exc())
        self.logger.info("~" * 30)

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpErrorr on %s', response.url)
            self.logger.error(f'Adding {response.url} to error_400_urls')
            self.error_400_urls.append({response.url, response.status})

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupErrorr on %s', request.url)
            self.logger.error(f'Adding {request.url} to error_DNS_urls')
            self.error_DNS_urls.append({request.url, failure.value.response.status})

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutErrorr on %s', request.url)
            self.logger.error(f'Adding {request.url} to error_urls')
            if request.url not in self.error_urls:
                self.error_urls.append({request.url})

            link_to_follow = failure.request.url

            self.logger.info('retrying on %s', link_to_follow)

            if link_to_follow not in self.error_urls:
                yield scrapy.Request(link_to_follow,
                                     dont_filter=True,
                                     headers={'x-irac-bot-access': 'true',
                                              'User-Agent': "hertz-sitemap-builder", },
                                     callback=self.parseErrorUrl,
                                     errback=self.retryPlaywrightRequest,
                                     cb_kwargs=dict(request_link=link_to_follow),
                                     meta=dict(
                                             playwright=True,
                                         )
                                     )


    async def errback(self, failure):
        self.logger.info("Inside errBack")
        self.logger.error(repr(failure))
        self.logger.info("failure in %s", failure.request.url)
        self.logger.error(traceback.format_exc())

        page = failure.request.meta["playwright_page"]
        await page.close()

    async def close(self, reason):
        """ handle logic at the closing of the spider"""

        self.logger.info("\n" + "self.error_urls")
        self.logger.info("#" * 50)
        for url in self.error_urls:
            self.logger.info(str(url))

        self.logger.info("\n" + "self.error_400_urls")
        self.logger.info("#" * 50)
        for url in self.error_400_urls:
            self.logger.info(str(url))

        self.logger.info("\n" + "self.error_DNS_urls")
        self.logger.info("#" * 50)
        for url in self.error_DNS_urls:
            self.logger.info(str(url))

        self.logger.info("\n" + "self.following_links")
        self.logger.info("#" * 50)
        for url in self.following_links:
            self.logger.info(str(url))

        self.logger.info("\n" + "self.error_500_urls")
        self.logger.info("#" * 50)
        for url in self.error_500_urls:
            self.logger.info(str(url))

        self.error_DNS_urls = []
        self.error_400_urls = []
        self.error_urls = []
        self.following_links = []
        self.links = []
        self.logger.info("closing spider")
