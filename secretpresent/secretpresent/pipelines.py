# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from typing import Tuple

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker, Session

from models.db_connect import session_local
from models.product import Product, ProductCategory, ShoppingCategory, NaverShoppingCategory
from models.marketplace import Marketplace

from models.product import NaverShoppingProduct


class SecretpresentPipeline:
    db: Session
    product: dict

    def open_spider(self, spider):
        self.db = session_local()
        self.product = {}

    def process_item(self, item: NaverShoppingProduct, spider):

        if item.product_id not in self.product:
            self.product[item.product_id] = item

        existed_product = (self.db.query(Product)
                           .filter(Product.marketplace_product_id == item.product_id)
                           .first())
        if existed_product:
            product = existed_product
            product.name = item.title
            product.price = item.price
            product.thumbnail_img_url = item.img_src
            product.marketplace = Marketplace.NAVER
            product.marketplace_product_id = item.product_id
            product.review_count = item.review_count
            product.brand_name = item.brand_name
            product.like_count = 0
            product.overall_rate = item.score_rate
            product.is_sold_out = False
            product.free_shipping = item.free_shipping

            product_categories = self.db.query(ProductCategory).filter(
                ProductCategory.product_id == product.id).all()

            category_ids = [item.shopping_category_id for item in product_categories]
            for category in item.categories:
                if category.id not in category_ids:
                    product_category = ProductCategory(
                        product_id=product.id,
                        shopping_category_id=category.id,
                    )
                    self.db.add(product_category)

            self.db.flush()

        else:
            product = Product(
                name=item.title,
                price=item.price,
                thumbnail_img_url=item.img_src,
                marketplace=Marketplace.NAVER,
                marketplace_product_id=item.product_id,
                review_count=item.review_count,
                brand_name=item.brand_name,
                like_count=0,
                overall_rate=item.score_rate,
                is_sold_out=False,
                free_shipping=item.free_shipping,
                buying_url=f"https://shopping.naver.com/gift/products/{item.product_id}"
            )
            self.db.add(product)
            self.db.flush()

            for category in item.categories:
                product_category = ProductCategory(
                    product_id=product.id,
                    shopping_category_id=category.id,
                )
                self.db.add(product_category)

        if item.idx == 1:
            category, child_category = item.categories
            if not category.child_categories:
                target_category_1 = self.db.query(NaverShoppingCategory).filter(
                    NaverShoppingCategory.id == category.id).first()
                target_category_1.image_url = item.img_src
            if not child_category.child_categories:
                target_category_2 = self.db.query(NaverShoppingCategory).filter(
                    NaverShoppingCategory.id == child_category.id).first()
                target_category_2.image_url = item.img_src

            self.db.commit()

        self.db.flush()

        # if item['marketplace'] == Marketplace.A29CM:

        #
        #     categoryInfo = item['frontCategoryInfo'][0]
        #
        #     product.categories = [
        #         ProductCategory(name = categoryInfo['categoryLargeName']),
        #         ProductCategory(name = categoryInfo['categoryMediumName']),
        #         ProductCategory(name = categoryInfo['categorySmallName'])
        #     ]
        #
        # elif item['marketplace'] == Marketplace.KAKAO:
        #     # product = Product(
        #     #     name = item['name'],
        #     #     price = item['price']['basicPrice'],
        #     #     thumbnail_img_url = item['imageUrl'],
        #     #     marketplace = item['marketplace'],
        #     #     marketplace_product_id = item['_id'],
        #     #     review_count = item['reviewCount'],
        #     #     like_count = item['wish']['wishCount'],
        #     #     overall_rate = item['reviewAverage'] * 20,
        #     #     is_sold_out = item['isSoldOut'],
        #     #     buying_url = f"https://product.29cm.co.kr/catalog/{item['id']}"
        #     # )
        #     return
        #
        #
        return {"test": "finish"}

    def close_spider(self, spider):
        self.db.commit()

        self.db.close()


class SecretpresentCategoryPipeline:
    db: Session
    product: dict

    def open_spider(self, spider):
        self.db = session_local()
        self.product = {}

    def process_item(self, item: ShoppingCategory, spider):
        existed_category: NaverShoppingCategory = self.db.query(NaverShoppingCategory).get(item.category_id)

        if existed_category:
            return item

        new_category = NaverShoppingCategory(
            id=item.category_id,
            name=item.category_name,
            parent_category_id=item.parent_category_id
        )

        self.db.add(new_category)
        self.db.flush()

    def close_spider(self, spider):
        self.db.commit()

        self.db.close()
