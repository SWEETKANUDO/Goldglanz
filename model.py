from dotenv import load_dotenv
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

app = Flask(__name__)

# ✅ Use PyMySQL for better compatibility

db = SQLAlchemy()

migrate = Migrate(app, db)

# ----------------- MODELS -----------------

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    cart_items = db.relationship("Cart", back_populates="user", cascade="all, delete")
    orders = db.relationship("Order", back_populates="user",  cascade="all, delete")

    def get_id(self):
        return str(self.user_id)  
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"
       

class Product(db.Model):
    __tablename__ = 'products'
    
    p_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_name = db.Column(db.String(255), nullable=False)
    p_image = db.Column(db.String(255), nullable=False)
    p_price = db.Column(db.Integer, nullable=False)
    p_description = db.Column(db.Text, nullable=False)
    p_category = db.Column(db.String(255), nullable = False)
    p_weight = db.Column(db.Integer, nullable = False)
    p_material = db.Column(db.String(255), nullable = False)

    # Relationships
    cart_items = db.relationship("Cart", back_populates="product",cascade = "all, delete-orphan")
    orders = db.relationship("Order", back_populates="product", cascade = "all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(p_id={self.p_id}, p_name='{self.p_name}', p_price={self.p_price})>"


class Cart(db.Model):
    __tablename__ = 'carts'
    
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('products.p_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    user = db.relationship("User", back_populates="cart_items")
    product = db.relationship("Product", back_populates="cart_items")
    
    def __repr__(self):
        return f"<Cart(cart_id={self.cart_id}, user_id={self.user_id}, p_id={self.p_id}, quantity={self.quantity})>"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.p_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Integer, nullable = False)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    product = db.relationship('Product', back_populates='orders')



class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.username}>'    

# ----------------- CREATE TABLES -----------------

# with app.app_context():
# #     db.drop_all()
#     db.create_all()
#     print("✅ Tables dropped and recreated with new fields.")
