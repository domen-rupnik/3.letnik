from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, BOOLEAN
from base import Base

class User(Base):
    __tablename__ = 'User_'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(30))
    user_surname = Column(String(30))
    user_email = Column(String(100))
    user_password = Column(String(300))

class Shop(Base):
    __tablename__ = 'Shop_'
    shop_name = Column(String(30), primary_key=True)
    shop_url = Column(String(30))

class Product(Base):
    __tablename__ ='Product_'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(30))
    product_image = Column(String(300))


class Products_Shop(Base):
    __tablename__ = 'Product_Shop_'
    product_shop_id = Column(Integer, primary_key=True)
    product_shop_product_id = Column(Integer, ForeignKey('Product_.product_id'))
    product_shop_shop_name = Column(String(30), ForeignKey('Shop_.shop_name'))
    product_shop_url = Column(String(300))
    product_shop_price = Column(DECIMAL)
    product_shop_discount = Column(DECIMAL)


class Price(Base):
    __tablename__ = 'Price_'
    price_id = Column(Integer, primary_key=True)
    price_product_shop_id = Column(Integer, ForeignKey('Product_Shop_.product_shop_product_id'))
    price_price = Column(Integer)
    price_date = Column(String(10))


class Users_Products(Base):
    __tablename__ = 'Users_Products_'
    users_products_user_id = Column(Integer, ForeignKey('User_.user_id'), primary_key=True)
    users_products_product_id = Column(Integer, ForeignKey('Product_.product_id'), primary_key=True)
    users_products_lower_reminder = Column(DECIMAL)
    users_products_upper_reminder = Column(DECIMAL)
    users_products_lower_condition = Column(BOOLEAN)
    users_products_upper_condition = Column(BOOLEAN)
    users_products_sent_email = Column(BOOLEAN)

