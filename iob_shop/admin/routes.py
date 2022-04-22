from wsgiref import validate
from flask import render_template, session, request, redirect, url_for, flash

from iob_shop import app, db, bcrypt
from .forms import RegistrationForm, LoginForm
from .models import User
from iob_shop.products.models import Product, Publisher, Category, Author
import os

@app.route('/admin')
def admin():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('admin/index.html', title='Admin page', products=products)

@app.route('/publishers')
def publishers():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = Publisher.query.order_by(Publisher.id.desc()).all()
    return render_template('admin/publishers.html', title='Publisher page', publishers=publishers)

@app.route('/authors')
def authors():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    authors = Author.query.order_by(Author.id.desc()).all()
    return render_template('admin/publishers.html', title='Author page', authors=authors)

@app.route('/categories')
def categories():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/publishers.html', title='Categories', categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.name.data}!! Thank you for registering', 'success')
        return redirect(url_for('admin'))
    return render_template('admin/register.html', form=form, title='Registeration page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Welcom {form.email.data}! You\'re loged in now', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong Password please try again', 'danger')
    return render_template('admin/login.html', form=form, title='Login Page')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))