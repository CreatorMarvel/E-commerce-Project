from config import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float, JSON
from flask_login import UserMixin


class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, password, email):
        self.password = password
        self.email = email


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


class Cart(db.Model):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    brand: Mapped[str] = mapped_column(String)

    def __int__(self, title, image, quantity, price, brand):
        self.title = title
        self.image = image
        self.quantity = quantity
        self.price = price
        self.brand = brand

    def __repr__(self):
        return f'<Item: {self.title}>'


class Products(db.Model):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    rating: Mapped[str] = mapped_column(JSON)
    gender: Mapped[str] = mapped_column(String)
    brand: Mapped[str] = mapped_column(String)

    def __init__(self, title, price, description, category, image, rating, gender, brand):
        self.title = title
        self.price = price
        self.description = description
        self.category = category
        self.image = image
        self.rating = rating
        self.gender = gender
        self.brand = brand

    def __repr__(self):
        return f'<Product: {self.title}>'
