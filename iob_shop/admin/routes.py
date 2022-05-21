from wsgiref import validate
from flask import render_template, session, request, redirect, url_for, flash

from iob_shop import app, db, bcrypt
from .forms import RegistrationForm, LoginForm
from .models import Admin
from iob_shop.books.models import Book, Publisher, Category, Author, Discount
from iob_shop.customers.models import SalesAmount, CustomerOrder
from datetime import datetime
import json
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
    return render_template('admin/publishers.html', title='Authors page', authors=authors)

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

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    #Doanh thu năm hiện tại
    curr_year=datetime.utcnow().year
    quarterSales=db.session.query(SalesAmount).filter_by(year=curr_year).first()
    sales=[int(quarterSales.quarter1),int(quarterSales.quarter2),int(quarterSales.quarter3),int(quarterSales.quarter4)]

    #Lượng người mua theo ngày trong tháng hiện tại
    curr_month=datetime.utcnow().month
    labels=[]
    quantity_customer_order=[]
    dict_order={}
    customer_order_day=db.session.query(db.func.count(CustomerOrder.customer_id), CustomerOrder.date_created).group_by(CustomerOrder.date_created).order_by(CustomerOrder.date_created).all()
    if customer_order_day != None:
        for i in customer_order_day:
            if(i[1].year==curr_year and i[1].month==curr_month):
                dict_order[str(i[1].day)]=0
        for i in customer_order_day:
            if(i[1].year==curr_year and i[1].month==curr_month):
                dict_order[str(i[1].day)]+=int(i[0])
    for key in dict_order.keys():
        labels.append(key)
        quantity_customer_order.append(dict_order[key])

    #Top sản phẩm bán chạy
    bestSaler=[]
    best_saler=db.session.query(Book.title,Book.sales_amount).order_by(Book.sales_amount.desc()).all()
    count=1
    if best_saler!=None:
        for tt, amount in best_saler:
            if count<=10:
                a=[count,tt,amount]
                bestSaler.append(a)
                count+=1
            else: break

    return render_template("books/dashboard.html",title="Dashboard", quarterSales=json.dumps(sales),labels=json.dumps(labels),quantity_customer_order=json.dumps(quantity_customer_order),bestSaler=bestSaler)
