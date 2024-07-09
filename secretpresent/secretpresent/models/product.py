from dataclasses import dataclass
import datetime
from typing import Tuple, List

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from .marketplace import Marketplace


class Base(DeclarativeBase):
    pass


def callable_func(obj):
    a = [str(e.value) for e in obj]
    return a


class ProductCategory(Base):
    __tablename__ = "product_category"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id = mapped_column(ForeignKey("product.id"))
    product = relationship("Product", back_populates="categories")
    shopping_category_id = mapped_column(ForeignKey("naver_shopping_category.id"))
    naver_shopping_category = relationship("NaverShoppingCategory")


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    brand_name: Mapped[str] = mapped_column(String)
    categories: Mapped[List[ProductCategory]] = relationship(ProductCategory, back_populates="product")
    price: Mapped[str] = mapped_column(Integer)
    thumbnail_img_url: Mapped[str] = mapped_column(String)
    buying_url: Mapped[str] = mapped_column(String)
    marketplace: Mapped[Marketplace] = mapped_column(
        Enum(Marketplace, values_callable=callable_func, native_enum=False))
    marketplace_product_id: Mapped[int] = mapped_column(BigInteger)
    review_count: Mapped[int] = mapped_column(Integer)
    like_count: Mapped[int] = mapped_column(Integer)
    overall_rate: Mapped[int] = mapped_column(Integer)
    free_shipping: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sold_out: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    modified_at: Mapped[datetime.datetime] = mapped_column(DateTime, onupdate=datetime.datetime.now)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now,
                                                         onupdate=datetime.datetime.now)


class NaverShoppingCategory(Base):
    __tablename__ = "naver_shopping_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    parent_category_id: Mapped[int] = mapped_column(Integer, ForeignKey("naver_shopping_category.id"))
    parent_category: Mapped["NaverShoppingCategory"] = relationship("NaverShoppingCategory",
                                                                    back_populates="child_categories", remote_side=[id])
    child_categories: Mapped[List["NaverShoppingCategory"]] = relationship("NaverShoppingCategory",
                                                                           back_populates="parent_category")


@dataclass
class NaverShoppingProduct:
    idx: int
    product_id: int
    img_src: str
    title: str
    price: int
    brand_name: str
    categories: Tuple[NaverShoppingCategory, NaverShoppingCategory]
    free_shipping: bool
    score_rate: int
    review_count: int


@dataclass
class ShoppingCategory:
    parent_category_id: int | None
    category_id: int
    category_name: str
