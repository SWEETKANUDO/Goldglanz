from functools import wraps
from operator import or_
from dotenv import load_dotenv
from flask import Flask, abort, render_template, request, flash, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from model import Cart, Contact, Order, User, Product, db
from flask_migrate import Migrate
from flask_login import UserMixin
import os

app = Flask(__name__)
app.secret_key = '9664852364'



load_dotenv()  # Load .env file

app = Flask(__name__)

# Get database URL from .env
database_uri = os.getenv("DATABASE_URL")
print("DEBUG DATABASE_URL:", database_uri)  # just to confirm

if not database_uri:
    raise ValueError("DATABASE_URL not found in environment variables")

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "ssl": True  # simple True works with Aiven
    }
}




db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    existing_admin = User.query.filter_by(email='neelpala28@gmail.com').first()
    if not existing_admin:
        password = 'Neel@1947'
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(username='neel', email='neelpala28@gmail.com', password=password_hash, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/estimate')
def estimate():
    return render_template('estimate.html')

@app.route('/shop', methods=['GET'])
def shop():
    # Get filters from query string (e.g., /shop?category=Ring&material=Gold&min_price=1000&max_price=5000)
    category = request.args.get('category[]')
    material = request.args.get('material[]')

    # Start base query
    query = Product.query

    # Apply filters dynamically
    if category:
        query = query.filter_by(p_category=category)
    if material:
        query = query.filter_by(p_material=material)
    
    products = query.all()
    return render_template('shop.html', products=products)


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    user_id = current_user.user_id
    carts = db.session.query(Cart, Product).join(Product, Cart.p_id == Product.p_id).filter(Cart.user_id == user_id).all()
    return render_template('cart.html', carts=carts)

@app.route('/add_to_cart/<int:p_id>', methods=['POST'])
@login_required
def add_to_cart(p_id):
    user_id = current_user.user_id
    quantity = int(request.form.get('quantity', 1))

    product = Product.query.get_or_404(p_id)
    # product_price = product.p_price
    # total_price = product.p_price * quantity

    existing = Cart.query.filter_by(user_id=user_id, p_id=p_id).first()

    if existing:
        existing.quantity += quantity
        # existing.total_price += total_price
    else:
        new_cart = Cart(
            user_id=user_id,
            p_id=p_id,
            quantity=quantity,
            # total_price=total_price
        )
        db.session.add(new_cart)

    db.session.commit()
    flash("Item added to cart successfully!", "success")
    return redirect('/cart')

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)

    if cart.user_id != current_user.user_id:
        flash("Unauthorized access", "danger")
        return redirect('/login')

    new_quantity = int(request.form['quantity'])
    cart.quantity = new_quantity
    # cart.total_price = cart.product.p_price * new_quantity  # Update total price
    db.session.commit()

    flash("Quantity updated!", "success")
    return redirect('/cart')

@app.route('/cart/remove/<int:cart_id>', methods=['POST', 'GET'])
@login_required
def remove_cart_item(cart_id):
    cart = Cart.query.get_or_404(cart_id)

    if cart.user_id != current_user.user_id:
        flash("Unauthorized", "danger")
        return redirect('/login')

    db.session.delete(cart)
    db.session.commit()
    flash("Item removed from cart", "danger")
    return redirect('/cart')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    username = request.form.get('username')
    email = request.form.get('email')
    message = request.form.get('message')

    new_contact = Contact(username=username, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()

    flash('Thank you for contacting us!', 'success')
    return redirect(url_for('contact'))

@app.route('/orders', methods=['GET'])
@login_required
def orders():
    user_id = current_user.user_id
    orders = db.session.query(Order, Product).join(Product, Order.product_id == Product.p_id).filter(Order.user_id == user_id).all()
    return render_template('orders.html', orders=orders)

@app.route('/orders/place', methods=['GET','POST'])
@login_required
def place_order():
    user_id = current_user.user_id
    carts = Cart.query.filter_by(user_id=user_id).all()

    for cart_item in carts:
        new_order = Order(
            user_id=user_id,
            product_id=cart_item.p_id,
            quantity=cart_item.quantity,
            total_price=cart_item.quantity * cart_item.product.p_price
        )
        db.session.add(new_order)

    # Cart.query.filter_by(user_id=user_id).delete()  # Clear cart
    db.session.commit()

    flash("Order placed successfully!", "success")
    return redirect('/orders')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login Successful!", "success")
            if user.is_admin:
                    return redirect('/admin')
            
            return redirect('/')
        
        else:
            flash("Invalid email or password", "danger")

    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        raw_password = request.form['password']

        hashed_password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect('/login')

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out", "danger")
    return redirect('/login')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dash():
    product = Product.query.all()
    return render_template('admin/dashboard.html', products=product)

@app.route('/admin/add',methods = ['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['p_name']
        image = request.form['p_image']
        price = request.form['p_price']
        description = request.form['p_description']
        weight  = request.form['p_weight']
        categoy  = request.form['p_category']
        material = request.form['p_material']

        new_product = Product(p_name=name, p_image=image, p_price=int(price), p_description=description,p_weight=weight,p_category=categoy,p_material = material)

        db.session.add(new_product)
        db.session.commit()

        flash("product added successfully","success")
        return redirect('/admin')

    return render_template('admin/add.html', )

@app.route('/admin/edit/<int:id>',methods = ['GET','POST'])
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.p_name = request.form['p_name']
        product.p_price = request.form['p_price']
        product.p_description = request.form['p_description']

        db.session.commit()
        flash("Product Updated successfull!","Success")  
        return redirect("/admin")
    
    return render_template('admin/edit.html',products=product)

@app.route('/admin/delete/<int:id>',methods = ['GET'])
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully!", "danger")
    return redirect("/admin")

@app.route('/admin/manage_orders')
@admin_required
def admin_orders():
    orders = Order.query.all()
    return render_template('admin/manage_orders.html', orders=orders)

@app.route('/admin/manage_user')
@admin_required
def manage_users():
     users = User.query.all()
     return render_template('admin/manage_user.html', users=users)

@app.route('/admin/contacts')
@login_required  # optional: ensure only logged-in admins can access
def admin_contacts():
    contacts = Contact.query.order_by(Contact.id.desc()).all()
    return render_template('admin/contact.html', contacts=contacts)

@app.route('/product/<int:p_id>')
def product_detail(p_id):
    product = Product.query.get_or_404(p_id)
    return render_template('product_details.html', product=product)

if __name__ == '__main__':
    app.run(debug=True, port=5501)
