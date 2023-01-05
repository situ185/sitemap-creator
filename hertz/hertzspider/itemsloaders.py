import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

class HertzURLLoader(ItemLoader):

    default_output_processor = TakeFirst()
    #price_in = MapCompose(lambda x: x.split("£")[-1])
    url_item_in = MapCompose(lambda x: 'https://www.hertz.com' + x )