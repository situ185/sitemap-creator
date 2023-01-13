# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from random import randint
from urllib.parse import urlencode

import requests
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

class HertzDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_HEADERS_ENDPOINT',
                                               'http://headers.scrapeops.io/v1/browser-headers?')
        self.scrapeops_fake_headers_active = settings.get('SCRAPEOPS_FAKE_HEADERS_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_headers_list()
        self._scrapeops_fake_headers_enabled()

    def _get_headers_list(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        json_response = response.json()
        self.headers_list = json_response.get('result', [])

    def _get_random_header(self):
        random_index = randint(0, len(self.headers_list) - 1)
        return self.headers_list[random_index]

    def _scrapeops_fake_headers_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == '' or self.scrapeops_fake_headers_active == False:
            self.scrapeops_fake_headers_active = False
        self.scrapeops_fake_headers_active = True

    def process_request(self, request, spider):
        random_header = self._get_random_header()
        for key, val in random_header.items():
            request.headers[key] = val
