import scrapy
from scrapy_playwright.page import PageMethod

import traceback



class HertzspiderSpider(scrapy.Spider):
    name = 'hertzspider'
    allowed_domains = ['hertz.com']
    
    def start_requests(self):
        yield scrapy.Request(f'https://{self.domain}/rentacar/reservation',
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                errback=self.errback,
                playwright_page_methods=[
                    PageMethod('wait_for_selector','div#container')
                    ]
            )
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        for link in response.css("a::attr('href')"):
            try:
                self.logger.info("Visiting %s",link.get())

                link_to_follow=link.get()
                yield response.follow(link_to_follow,
                                        callback=self.parseURL,
                                        errback=self.parseError,
                                        cb_kwargs=dict(request_link=link_to_follow),
                                        meta=dict(
                                            playwright=True,
                                            playwright_include_page=True,
                                            playwright_page_methods=[
                                                PageMethod('wait_for_selector','div#container')
                                                ]
                                        )
                                    )
            except Exception:
                print(traceback.format_exc())
                self.logger.error(repr(Exception))
                yield{
                    'error':"error fetching " +link.get(),
                    'status':response.status
                }
    

    async def parseURL(self,response,request_link):
       try:
           self.logger.info("response is  %s",response.url)
           self.logger.info("request_link is %s",request_link)

           yield{
               'loc':request_link
           }  
       except:
           yield{
               'loc':"error"
           } 

        #url_item=HertzItem()
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
        

    async def parseError(self,failure,request_link):
        yield{
            'failure_url':request_link,
            'url':failure.url,
            'status':failure.status
        }

    async def errback(self,failure):
        page=failure.request.meta["playwright_page"]
        await page.close()

