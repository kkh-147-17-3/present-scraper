import scrapy
import json
import time

from secretpresent.models.marketplace import Marketplace

class KakaoSpider(scrapy.Spider):
    name = "kakao"
    allowed_domains = ["gift.kakao.com"]

    def start_requests(self):
        base_url = "https://gift.kakao.com/a/v2/search/products"
        current_timestamp = int(time.time())
        urls = [f'{base_url}?query=전구&page={x}&_={current_timestamp}' for x in range(1,6)]
        for url in urls:
            print("------------------------" + url + "---------------------------")
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = json.loads(response.text)["products"]
        for product in products['contents']:
            product['_id'] = product['id']
            product['marketplace'] = Marketplace.KAKAO
            yield product
        
