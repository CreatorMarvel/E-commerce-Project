from flask import render_template, request, redirect, url_for, flash
from config import app, db, bcrypt
from models import Products, User, Cart
from blueprints.admin.source import admin
from config import login_manager
from flask_login import current_user, login_user, logout_user, login_required
from dotenv import load_dotenv, find_dotenv
import stripe
import smtplib
import os

app.register_blueprint(admin, url_prefix='/admin')

file_path = find_dotenv()
load_dotenv(file_path)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


stripe.api_key = os.environ.get('STRIPE_API')
YOUR_DOMAIN = 'http://localhost:5000'


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': '{{PRICE_ID}}',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)


def calculate_total():
    subtotal, delivery, carts = 0, 0, 0

    cart_items = Cart.query.all()
    for item in cart_items:
        subtotal += item.price * item.quantity
        carts += item.quantity
    total = delivery + subtotal
    return {'total': total, 'delivery': delivery, 'subtotal': subtotal, 'carts': carts, 'cart_items': cart_items}


@app.route('/')
def index():
    return render_template('index.html', is_authenticated=current_user.is_authenticated,
                           carts=calculate_total().get('carts'))


@app.route('/search')
def search():
    q = request.args.get('q')
    if q:
        results = Products.query.filter(Products.title.icontains(q) | Products.description.icontains(q)).all()
        return render_template('search.html', results=results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        is_exist = db.session.execute(db.select(User).where(User.username == username)).scalar()
        if is_exist and is_exist.password == password:
            login_user(is_exist)
            return redirect(url_for('index'))
        else:
            flash('Username or password is incorrect!')
            return redirect(url_for('login'))
    return render_template('login.html', carts=calculate_total().get('carts'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        if password != password_repeat:
            flash('Passwords don\'t match. Passwords must be the same!')
            return redirect(url_for('register'))

        if db.session.execute(db.select(User).where(User.username == username)).scalar():
            flash('Username is already in-use!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', carts=calculate_total().get('carts'))


@app.route('/products')
def products():
    all_products = Products.query.all()
    categories = set([_.category for _ in Products.query.all()])
    genders = set([_.gender for _ in Products.query.all()])
    brands = set([_.brand for _ in Products.query.all()])

    return render_template('products.html',
                           products=all_products,
                           categories=categories,
                           genders=genders,
                           brands=brands,
                           is_authenticated=current_user.is_authenticated,
                           carts=calculate_total().get('carts')
                           )


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    return render_template('cart.html',
                           carts=calculate_total().get('carts'),
                           cart_items=calculate_total().get('cart_items'),
                           total=round(calculate_total().get('total'), 2),
                           delivery=round(calculate_total().get('delivery'), 2),
                           subtotal=round(calculate_total().get('subtotal'), 2))


@app.route('/add-cart/<int:idx>', methods=['GET', 'POST'])
def add_product_to_cart(idx):
    product = db.session.execute(db.select(Cart).where(Cart.id == idx)).scalar()
    if product:
        product.quantity += 1
        db.session.commit()
        flash('Product  added to cart!')
        return redirect(url_for('products'))

    item = db.session.execute(db.select(Products).where(Products.id == idx)).scalar()
    print(item.title)
    if item:
        try:
            new_item = Cart(title=item.title, image=item.image, quantity=1, price=item.price)
            db.session.add(new_item)
            db.session.commit()
            flash('Product  added to cart!')
            return redirect(url_for('products'))
        except Exception as e:
            return str(e)
    else:
        flash('Product  doesnt exist!')
        return redirect(url_for('products'))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route('/delete-cart/<int:idx>')
def delete_cart_item(idx):
    print(idx)
    product = db.session.execute(db.select(Cart).where(Cart.id == idx)).scalar()
    db.session.delete(product)
    db.session.commit()
    flash('Product  deleted!')
    return redirect(url_for('cart'))


@app.route('/decrease-increase/<int:idx>/<string:action>')
def change_quantity(idx, action):
    product = db.session.execute(db.select(Cart).where(Cart.id == idx)).scalar()
    if action == 'decrease':
        product.quantity -= 1
    else:
        product.quantity += 1
    flash('Product  edited!')
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/send', methods=['POST'])
def send_email():
    user_email = request.form.get('email')
    user_name = request.form.get('name')
    user_phone = request.form.get('phone')
    subject = request.form.get('subject')
    user_message = request.form.get('comment')

    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(
            user=os.environ.get('EMAIL_USERNAME'),
            password=os.environ.get('EMAIL_PASSWORD')
        )
        connection.sendmail(
            to_addrs=os.environ.get('EMAIL_USERNAME'),
            from_addr=os.environ.get('EMAIL_USERNAME'),
            msg=f'Subject:Public website Review - "{subject}"\n\nFrom:{user_name}\nEmail:{user_email}\nPhone:{user_phone}\nMessage:{user_message}'.encode(
                'utf-8')
        )
    flash('Message successfully sent!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=3000, debug=False)
