from flask import Blueprint, render_template, redirect, url_for, flash
from models import Products, Admin
from config import db, app
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, StringField, FloatField, IntegerField
from flask_login import login_required, login_user
from config import bcrypt

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


class NewProductForm(FlaskForm):
    title = StringField('Product Title')
    price = FloatField('Product Price')
    description = StringField('Product Description')
    category = StringField('Product Category')
    image = StringField('Product Image (URL)')
    rating_rate = FloatField('Product Rating (Rate)')
    rating_count = IntegerField('Product Rating (Count)')
    gender = StringField('Gender')
    brand = StringField('Brand')
    add = SubmitField('Add')


class AdminLoginForm(FlaskForm):
    username = StringField('Enter your username', validators=[DataRequired()])
    password = StringField('Enter your password', validators=[DataRequired()])
    login = SubmitField('Login')


@admin.route('/', methods=['GET', 'POST'])
def index():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin_password = form.data.get('password')
        admin_username = form.data.get('username')

        if not admin_password or not admin_username:
            flash('Please enter all fields!')
            return redirect(url_for('admin.index'))
        else:

            user = db.session.execute(db.select(Admin).where(Admin.username == admin_username)).scalar()

            if user:
                if user.username == admin_username and bcrypt.check_password_hash(user.password, admin_password):
                    login_user(user)
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Invalid credentials. Please enter correct email or password!')
                    return redirect(url_for('admin.index'))
            else:
                flash('You are not an admin user!')
                return redirect(url_for('admin.index'))
    return render_template('home.html', form=form)


@admin.route('/dashboard')
def dashboard():
    all_products = Products.query.all()
    return render_template('dashboard.html', products=all_products)


@admin.route('/delete/<int:idx>')
@login_required
def delete_product(idx):
    current_product = db.session.execute(db.select(Products).where(Products.id == idx)).scalar()
    db.session.delete(current_product)
    db.session.commit()
    return redirect(url_for('admin.home'))


@admin.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = NewProductForm()
    if form.validate_on_submit():
        new_product = Products(
            title=form.title.data,
            price=form.price.data,
            description=form.description.data,
            category=form.category.data,
            image=form.image.data,
            gender=form.gender.data,
            brand=form.brand.data,
            rating={'rate': form.rating_rate.data, 'count': form.rating_count.data}
        )
        try:
            db.session.add(new_product)
            db.session.commit()
        except Exception as err:
            return str(err)
        else:
            return redirect(url_for('admin.home'))
    return render_template('product.html', form=form)
