from wsgiref import validate
from flask import render_template, session, request, redirect, url_for, flash

from iob_shop import app, db, bcrypt
from .forms import RegistrationForm, LoginForm
from .models import Admin
from iob_shop.books.models import Book, Publisher, Category, Author, Discount
import os

@app.route('/admin')
def admin():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    books = db.session.query(Book).all()
    return render_template('admin/index.html', title='Admin page', books=books)

@app.route('/publishers')
def publishers():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = db.session.query(Publisher).order_by(Publisher.id.desc()).all()
    return render_template('admin/publishers.html', title='Publisher page', publishers=publishers)

@app.route('/authors')
def authors():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    authors = db.session.query(Author).order_by(Author.id.desc()).all()
    return render_template('admin/publishers.html', title='Author page', authors=authors)

@app.route('/categories')
def categories():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    categories = db.session.query(Category).order_by(Category.id.desc()).all()
    return render_template('admin/publishers.html', title='Categories page', categories=categories)

@app.route('/discounts')
def discounts():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    discounts = db.session.query(Discount).order_by(Discount.id.desc()).all()
    return render_template('admin/publishers.html', title='Discount page', discounts=discounts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        admin = Admin(name=form.name.data, adminname=form.adminname.data, email=form.email.data,
                    password=hash_password)
        db.session.add(admin)
        db.session.commit()
        flash(f'Welcome {form.name.data}!! Thank you for registering', 'success')
        return redirect(url_for('admin'))
    return render_template('admin/register.html', form=form, title='Registeration page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        admin = db.session.query(Admin).filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Welcome {form.email.data}! You\'re loged in now', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong email or password please try again', 'danger')
    return render_template('admin/login.html', form=form, title='Login Page')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))
