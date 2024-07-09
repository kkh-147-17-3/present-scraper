import scrapy
import json

from secretpresent.models.marketplace import Marketplace


class A29cmCategorySpider(scrapy.Spider):
    name = "29cm_category"
    allowed_domains = ["https://cache.29cm.co.kr"]

    def start_requests(self):
        base_url = "https://cache.29cm.co.kr/item/category"
        for url in urls:
            urls = [f'{base_url}?query=전구&page={x}&_={current_timestamp}' for x in range(1,6)]
            print("------------------------" + url + "---------------------------")
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response, **kwargs):
        json_response = json.loads(response.text)
        if json_response['result'] != "SUCCESS":
            raise Exception("Not successful")

        for product in json_response['data']:
            product['marketplace'] = Marketplace.A29CM
            yield product
