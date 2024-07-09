import scrapy
import json

from secretpresent.models.marketplace import Marketplace


class A29cmSpider(scrapy.Spider):
    name = "29cm"
    allowed_domains = ["search-api.29cm.co.kr"]
    start_urls = [
        "https://search-api.29cm.co.kr/api/v4/products?keyword=%EC%A0%84%EA%B5%AC&brands=&categoryLargeCode"
        "=&categoryMediumCode=&categorySmallCode=&isFreeShipping=&isDiscount=&minPrice=&maxPrice=&colors=&limit=50"
        "&offset=0&sort=latest&gender=&excludeSoldOut="]

    def parse(self, response, **kwargs):
        json_response = json.loads(response.text)
        if json_response['result'] != "SUCCESS":
            raise Exception("Not successful")

        for product in json_response['data']:
            product['marketplace'] = Marketplace.A29CM
            yield product
