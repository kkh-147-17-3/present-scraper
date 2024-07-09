import scrapy
from secretpresent.categories import categories

from secretpresent.models.product import NaverShoppingProduct, NaverShoppingCategory


class NaverShoppingSpider(scrapy.Spider):
    name = "navershopping"

    categories: list[NaverShoppingCategory] = categories

    def start_requests(self):
        for category in self.categories:

            object_categories = category.child_categories + sum([child.child_categories for child in
                                                                category.child_categories if child.child_categories],
                                                               [])

            if not category.child_categories:
                object_categories += category

            for object_category in object_categories:
                url = f"https://shopping.naver.com/gift/category?menu={object_category.id}"
                print("------------------------" + url + "---------------------------")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "category": (category, object_category),
                        "playwright": True,
                        "playwright_include_page": True
                    },
                    errback=self.errback
                )

    async def parse(self, response, **kwargs):
        page = response.meta["playwright_page"]
        try:
            for i in range(10):
                await page.mouse.wheel(0, 150000)
                await page.wait_for_selector("//div[contains(@class, 'categoryPageResponsive_wrap_product')]")

                page_content = await page.content()
                items = scrapy.Selector(text=page_content).xpath(
                    "//ul[contains(@class, 'productCardListResponsive_product_card_list_responsive')]/li")

                for idx, item in enumerate(items):
                    product_id = int(item.xpath(".//@id").get())
                    img_src = item.xpath(".//img[contains(@class, 'productCardResponsive_image')]/@src").get()
                    product_name = item.xpath(".//strong[contains(@class, 'productCardResponsive_title')]/text()").get()
                    price = item.xpath(".//span[contains(@class, 'productCardResponsive_number')]/text()").get()
                    tags = item.xpath(".//span[contains(@class, 'productCardResponsive_tag')]/text()").getall()
                    free_shipping = True if "무료배송" in tags else False
                    brand_name = item.xpath(".//a[contains(@class, 'productCardResponsive_store_link')]/text()").get()
                    score_rate = item.xpath(".//span[contains(@class, 'productCardResponsive_score')]/text()").get()
                    review_count = item.xpath(".//div[contains(@class, 'productCardResponsive_wrap_review')]"
                                              "/span[contains(@class, 'productCardResponsive_text')][last()]/span/text()").get()

                    curr_child: NaverShoppingCategory
                    curr_category: NaverShoppingCategory
                    curr_category, curr_child = response.meta["category"]
                    yield NaverShoppingProduct(
                        idx=idx + i,
                        product_id=int(product_id),
                        img_src=img_src,
                        brand_name=brand_name,
                        title=product_name,
                        categories=(curr_category, curr_child),
                        free_shipping=free_shipping,
                        score_rate=None if score_rate is None else int(float(score_rate) * 20),
                        review_count=None if review_count is None else int(
                            review_count.replace(',', '').replace('+', '')),
                        price=int(price.replace(',', ''))
                    )
        except Exception as e:
            self.logger.error(f"An error occurred during parsing: {str(e)}")
        finally:
            await page.close()

        # cate_nums = list(map(lambda x: x.split(' ')[0].split(':')[2], cate_btns.xpath('./@class').getall()))
        # cate_text = cate_btns.xpath("./text()").getall()
        #
        # parent_category_num = response.url.split('menu=')[1].split('&')[0]
        # parent_category_name = self.categories[parent_category_num]
        #
        # for (num, text) in zip(cate_nums, cate_text):
        #     if text == "전체":
        #         continue
        #     yield {
        #         "parent_category_num": parent_category_num,
        #         "parent_category_name": parent_category_name,
        #         "category_num": num, ul
        #         "category_name": text
        #     }

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
