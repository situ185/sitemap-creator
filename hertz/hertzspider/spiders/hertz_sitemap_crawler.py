# import scrapy
# from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy_playwright.page import PageMethod
# import logging
# import traceback
# from array import array
#
# logging.basicConfig(level=logging.CRITICAL, filename="../hertz/hertzspider/new_outputs/log_spider2.log")
#
#
# def set_playwright_true(request, response):
#     request.meta["playwright"] = True
#     request.meta["playwright_include_page"] = True,
#     request.meta["playwright_page_methods"] = [PageMethod('wait_for_selector', 'div#container')]
#     return request
#
#
# class HertzSitemapCrawlerSpider(CrawlSpider):
#     name = 'hertz_sitemap_crawler'
#     allowed_domains = ['hertz.com']
#
#     custom_settings = {
#         'FEEDS': {'../hertz/hertzspider/new_outputs/output_spider2.xml': {"format": 'xml'}},
#         "LOG_LEVEL": "INFO",
#     }
#
#     def start_requests(self):
#         yield scrapy.Request('https://www.hertz.com/rentacar/reservation',
#                              meta=dict(
#                                  playwright=True,
#                                  playwright_include_page=True,
#                                  errback=self.errback,
#                                  playwright_page_methods=[
#                                      PageMethod('wait_for_selector', 'div#container'),
#                                      PageMethod("wait_for_timeout", float(10000))
#                                  ]
#                              )
#                              )
#
#     rules = [
#         Rule(LinkExtractor(deny=['/p/','/A-thou-doe-prospeeceiud-accome-Hauen-heeleepell'],
#                            deny_domains=['salesforceliveagent.com', 'google-analytics.com', 'analytics.google.com',
#                                          'c.clicktale.net'], allow_domains=['www.hertz.com'],
#                            unique=True), callback='parse_item', follow=True,
#              process_request=set_playwright_true)
#     ]
#
#     async def parse_item(self, response):
#         page = response.meta["playwright_page"]
#
#         self.logger.info("crawling " + response.url)
#         if response.status == 200:
#             yield {
#                 'loc': response.url
#             }
#             try:
#                 self.logger.info("closing " + response.url)
#                 await page.close()
#             except Exception as e:
#                 self.logger.error(f"Failed to close browser context: {str(e)}")
#             finally:
#                 await page.close()
#                 #await page.context.close()
#         # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
#         # item['name'] = response.xpath('//div[@id="name"]').get()
#         # item['description'] = response.xpath('//div[@id="description"]').get()
#
#     async def errback(self, failure):
#         page = failure.request.meta["playwright_page"]
#
#         self.logger.error("Inside parseError")
#         self.logger.error(repr(failure))
#         self.logger.info("failure in  %s", failure.request.cb_kwargs['request_link'])
#         self.logger.error(traceback.format_exc())
#         try:
#             await page.close()
#         except Exception as e:
#             self.logger.error(f"Failed to close browser context: {str(e)}")
#         finally:
#             await page.close()
#             #await page.context.close()
