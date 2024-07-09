import scrapy
import json
import time

from scrapy_playwright.page import PageMethod

from secretpresent.models.product import NaverShoppingProduct, ShoppingCategory


class NaverShoppingCategorySpider(scrapy.Spider):
    name = "navershoppingcategory"
    start_url = "https://shopping.naver.com/gift/home"
    task_queue = []
    custom_settings = {
        'ITEM_PIPELINES': {
            "secretpresent.pipelines.SecretpresentCategoryPipeline": 300,
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse,
            meta={
                'depth': 0,
                'type': None,
                'grand_parent_id': None,
                'grand_parent_name': None,
                'parent_id': None,
                'parent_name': None,
                'current_id': None,
                'current_name': None,
            }
        )

    async def parse(self, response, **kwargs):
        depth = response.meta['depth']
        grand_parent_id = response.meta['grand_parent_id']
        grand_parent_name = response.meta['grand_parent_name']
        type = response.meta['type']
        parent_id = response.meta['parent_id']
        parent_name = response.meta['parent_name']

        current_id = response.meta['current_id']
        current_name = response.meta['current_name']
        if depth == 0:
            section_1, section_2 = response.xpath("//ul[contains(@class, 'imageCategoryResponsive_set_list__pldJo')]")

            section_1_category_classnames = section_1.xpath(".//button/@class").getall()
            section_1_category_names = section_1.xpath(".//button//span/text()").getall()

            section_2_category_classnames = section_2.xpath(".//button/@class").getall()
            section_2_category_names = section_2.xpath(".//button//span/text()").getall()

            section_1_category_ids = [classnames.split(' ')[0].split(":").pop() for classnames in
                                      section_1_category_classnames]
            section_2_category_ids = [classnames.split(' ')[0].split(":").pop() for classnames in
                                      section_2_category_classnames]

            for category_id, name in zip(section_1_category_ids, section_1_category_names):
                if name == '전체':
                    continue
                yield scrapy.Request(
                    url=f"https://shopping.naver.com/gift/category?menu={category_id}",
                    callback=self.parse,
                    meta={
                        'depth': 1,
                        'type': None,
                        'grand_parent_id': None,
                        'grand_parent_name': None,
                        'parent_id': None,
                        'parent_name': None,
                        'current_id': category_id,
                        'current_name': name
                    }
                )

            for category_id, name in zip(section_2_category_ids, section_2_category_names):
                if name == '전체':
                    continue
                yield scrapy.Request(
                    url=f"https://shopping.naver.com/gift/category?menuTab=PRODUCT&menu={category_id}",
                    callback=self.parse,
                    meta={
                        'depth': 1,
                        'type': 'PRODUCT',
                        'grand_parent_id': None,
                        'grand_parent_name': None,
                        'parent_id': None,
                        'parent_name': None,
                        'current_id': category_id,
                        'current_name': name
                    }
                )
        elif depth == 1:
            category_classnames = response.xpath(
                "//li[contains(@class, 'tagCategoryResponsive_list__rgT2Q')]/button/@class").getall()
            category_names = response.xpath(
                "//li[contains(@class, 'tagCategoryResponsive_list__rgT2Q')]/button/text()").getall()

            category_ids = [classnames.split(' ')[0].split(":").pop() for classnames in category_classnames]
            for category_id, name in zip(category_ids, category_names):
                if name == '전체':
                    yield ShoppingCategory(None, current_id, current_name)
                    continue
                yield scrapy.Request(
                    url=f"https://shopping.naver.com/gift/category?{'menuTab=PRODUCT&' if type is not None else ''}menu={category_id}",
                    callback=self.parse,
                    meta={
                        'depth': 2,
                        'type': type,
                        'grand_parent_id': None,
                        'grand_parent_name': None,
                        'parent_id': current_id,
                        'parent_name': current_name,
                        'current_id': category_id,
                        'current_name': name
                    }
                )
        elif depth == 2:
            category_classnames = response.xpath(
                "//li[contains(@class, 'textCategoryResponsive_list__IoVgP')]/button/@class").getall()
            category_names = response.xpath(
                "//li[contains(@class, 'textCategoryResponsive_list__IoVgP')]/button/text()").getall()

            category_ids = [classnames.split(' ')[0].split(":").pop() for classnames in category_classnames]
            for category_id, name in zip(category_ids, category_names):
                if name == '전체':
                    yield ShoppingCategory(parent_id, current_id, current_name)
                    continue
                yield scrapy.Request(
                    url=f"https://shopping.naver.com/gift/category?{'menuTab=PRODUCT&' if type is not None else ''}menu={category_id}",
                    callback=self.parse,
                    meta={
                        'depth': 3,
                        'type': type,
                        'grand_parent_id': parent_id,
                        'grand_parent_name': parent_name,
                        'parent_id': current_id,
                        'parent_name': current_name,
                        'current_id': category_id,
                        'current_name': name
                    }
                )
        else:
            yield ShoppingCategory(parent_id, current_id, current_name)

    # for item in items:
    #     product_id = item.xpath(".//@id").get()
    #     img_src = item.xpath(".//img[contains(@class, 'productCardResponsive_image')]/@src").get()
    #     product_name = item.xpath(".//strong[contains(@class, 'productCardResponsive_title')]/text()").get()
    #     price = item.xpath(".//span[contains(@class, 'productCardResponsive_number')]/text()").get()
    #     tags = item.xpath(".//span[contains(@class, 'productCardResponsive_tag')]/text()").getall()
    #     free_shipping = True if "무료배송" in tags else False
    #     score_rate = item.xpath(".//span[contains(@class, 'productCardResponsive_score')]/text()").get()
    #     review_count = item.xpath(".//div[contains(@class, 'productCardResponsive_wrap_review')]"
    #                               "/span[contains(@class, 'productCardResponsive_text')][last()]/span/text()").get()
    #
    #         yield NaverShoppingProduct(
    #             product_id=product_id,
    #             img_src=img_src,
    #             title=product_name,
    #             free_shipping=free_shipping,
    #             score_rate=score_rate,
    #             review_count=review_count,
    #             price=price
    #         )

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
