from click import File
from flask import redirect, request, url_for, render_template, flash, session, current_app
from flask_login import current_user
from sqlalchemy import func, null
from iob_shop import db, app, photos, search
from iob_shop.admin.routes import publishers
from .models import Author_write_book, Book_belongs_to_category, Book_discount, Publisher, Category, Author, Book, Discount
from .forms import Addbook
import secrets, os
from datetime import datetime

def publishers():
    publishers = db.session.query(Publisher).join(Book, (Publisher.name==Book.Pname)).all()
    return publishers

def categories():
    categories = db.session.query(Category).join(Book_belongs_to_category, (Category.name==Book_belongs_to_category.category_name)).all()
    return categories

def authors():
    authors = db.session.query(Author).join(Author_write_book, (Author.phone_num==Author_write_book.Aphone_num)).all()
    return authors

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    books = db.session.query(Book).filter(Book.stock > 0).paginate(page=page, per_page=12)
    publishers = db.session.query(Publisher).join(Book, (Publisher.name==Book.Pname)).all()
    categories = db.session.query(Category).join(Book_belongs_to_category, (Category.name==Book_belongs_to_category.category_name)).all()
    authors = db.session.query(Author).join(Author_write_book, (Author.phone_num==Author_write_book.Aphone_num)).all()
    discounts = db.session.query(Discount).join(Book_discount, (Discount.id==Book_discount.discount_id)).all()
    author_write_book = dict()
    book_belongs_to_category = dict()
    book_discount = dict()
    
    for book in books.items:
        squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
        author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
        squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
        category = db.session.query(Category).filter(Category.name.in_(squery)).all()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()
        author_write_book[book.ISBN] = author
        book_belongs_to_category[book.ISBN] = category
        book_discount[book.ISBN] = [int(discount[0]*100), book.price*(1 - discount[0])] if discount[0] else [0, book.price]
    return render_template('books/index.html', books=books, publishers=publishers, categories=categories, authors=authors, discounts=discounts, title='Home',
                           author_write_book=author_write_book, book_belongs_to_category=book_belongs_to_category, book_discount=book_discount)
    
@app.route('/result')
def result():
    page = request.args.get('page', 1, type=int)
    searchword = request.args.get('q')
    if searchword:
        books = db.session.query(Book).filter(Book.title.contains(searchword) | Book.shortdesc.contains(searchword)).paginate(page=page, per_page=15)
    else:
        books = db.session.query(Book).filter(Book.stock > 0).paginate(page=page, per_page=15)
    publishers = db.session.query(Publisher).join(Book, (Publisher.name==Book.Pname)).all()
    categories = db.session.query(Category).join(Book_belongs_to_category, (Category.name==Book_belongs_to_category.category_name)).all()
    authors = db.session.query(Author).join(Author_write_book, (Author.phone_num==Author_write_book.Aphone_num)).all()
    discounts = db.session.query(Discount).join(Book_discount, (Discount.id==Book_discount.discount_id)).all()
    author_write_book = dict()
    book_belongs_to_category = dict()
    book_discount = dict()
    for book in books.items:
        squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
        author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
        squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
        category = db.session.query(Category).filter(Category.name.in_(squery)).all()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()
        author_write_book[book.ISBN] = author
        book_belongs_to_category[book.ISBN] = category
        book_discount[book.ISBN] = [int(discount[0]*100), book.price*(1 - discount[0])] if discount[0] else [0, book.price]
    return render_template('books/index.html', books=books, publishers=publishers, categories=categories, authors=authors, discounts=discounts, title=f"'{searchword}'",
                           author_write_book=author_write_book, book_belongs_to_category=book_belongs_to_category, book_discount=book_discount)

@app.route('/publisher/<int:id>')
def get_publisher(id):
    page = request.args.get('page', 1, type=int)
    pname = db.session.query(Publisher).filter_by(id=id).first_or_404().name
    pbypublisher = db.session.query(Book).filter_by(Pname=pname).paginate(page=page, per_page=20)
    author_write_book = dict()
    book_belongs_to_category = dict()
    book_discount = dict()
    for book in pbypublisher.items:
        squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
        author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
        squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
        category = db.session.query(Category).filter(Category.name.in_(squery)).all()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()
        author_write_book[book.ISBN] = author
        book_belongs_to_category[book.ISBN] = category
        book_discount[book.ISBN] = [int(discount[0]*100), book.price*(1 - discount[0])] if discount[0] else [0, book.price]
    return render_template('books/index.html', books=pbypublisher, title=pname, author_write_book=author_write_book, book_belongs_to_category=book_belongs_to_category, book_discount=book_discount, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/addpublisher', methods=['GET', 'POST'])
def addpublisher():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getpublisher = request.form.get('publisher')
        getphone = request.form.get('phone')
        getid =request.form.get('id')
        publisher = Publisher(name=getpublisher, phone_num=getphone, id=getid)
        db.session.add(publisher)
        flash(f'The Publisher {getpublisher} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addpublisher'))
    return render_template('books/addpublisher.html', publisherss='publisherss', publishers=publishers(), categories=categories(), authors=authors())


@app.route('/updatepublisher/<int:id>', methods=['GET', 'POST'])
def updatepublisher(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updatepublisher = db.session.query(Publisher).filter_by(id=id).first_or_404()
    publisher = request.form.get('publisher')
    getphone = request.form.get('phone')
    if request.method == 'POST':
        updatepublisher.name = publisher
        updatepublisher.phone_num = getphone
        flash('Your publisher has been updated', 'success')
        db.session.commit()
        return redirect(url_for('publishers'))
        
    return render_template('books/updatepublisher.html', title='Update publisher page', updatepublisher=updatepublisher, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/deletepublisher/<int:id>', methods=['POST'])
def deletepublisher(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    publisher = db.session.query(Publisher).filter_by(id=id).first_or_404()
    if request.method == 'POST':
        db.session.delete(publisher)
        flash(f'The publisher {publisher.name} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('publishers'))
    flash(f'The publisher {publisher.name} can\'t be deleted', 'warning')
    return redirect(url_for('publishers'))

@app.route('/category/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    category_name = db.session.query(Category).filter_by(id=id).first_or_404().name
    pbycategory = db.session.query(Book).join(Book_belongs_to_category, (Book.ISBN==Book_belongs_to_category.ISBN)).filter_by(category_name=category_name).paginate(page=page, per_page=20)
    author_write_book = dict()
    book_belongs_to_category = dict()
    book_discount = dict()
    for book in pbycategory.items:
        squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
        author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
        squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
        category = db.session.query(Category).filter(Category.name.in_(squery)).all()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()
        author_write_book[book.ISBN] = author
        book_belongs_to_category[book.ISBN] = category
        book_discount[book.ISBN] = [int(discount[0]*100), book.price*(1 - discount[0])] if discount[0] else [0, book.price]
    return render_template('books/index.html', books=pbycategory, title=category_name, author_write_book=author_write_book, book_belongs_to_category=book_belongs_to_category, book_discount=book_discount, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getcategory = request.form.get('category')
        getid = request.form.get('id')
        category = Category(name=getcategory, id=getid)
        db.session.add(category)
        flash(f'The Category {getcategory} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcategory'))
    return render_template('books/addpublisher.html', publishers=publishers(), categories=categories(), authors=authors())

@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updatecategory = db.session.query(Category).filter_by(id=id).first_or_404()
    category = request.form.get('category')
    if request.method == 'POST':
        updatecategory.name = category
        flash('Your category has been updated', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    
    return render_template('books/updatepublisher.html', title="Update category page", updatecategory=updatecategory, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    
    category = db.session.query(Category).filter_by(id=id).first_or_404()
    if request.method == 'POST':
        db.session.delete(category)
        flash(f'The category {category.name} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    flash(f'The publisher {category.name} can\'t be deleted', 'warning')
    return redirect(url_for('categories'))

@app.route('/author/<int:id>')
def get_author(id):
    page = request.args.get('page', 1, type=int)
    author = db.session.query(Author).filter_by(id=id).first_or_404()
    authorname = author.Fname + (author.Mname if author.Mname else '') + author.Lname
    pbyauthor = db.session.query(Book).join(Author_write_book, (Book.ISBN==Author_write_book.ISBN)).filter_by(Aphone_num=author.phone_num).paginate(page=page, per_page=20)
    author_write_book = dict()
    book_belongs_to_category = dict()
    book_discount = dict()
    for book in pbyauthor.items:
        squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
        author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
        squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
        category = db.session.query(Category).filter(Category.name.in_(squery)).all()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()
        author_write_book[book.ISBN] = author
        book_belongs_to_category[book.ISBN] = category
        book_discount[book.ISBN] = [int(discount[0]*100), book.price*(1 - discount[0])] if discount[0] else [0, book.price]
    return render_template('books/index.html', books=pbyauthor, title=authorname, author_write_book=author_write_book, book_belongs_to_category=book_belongs_to_category, book_discount=book_discount, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/addauthor', methods=['GET', 'POST'])
def addauthor():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getid = request.form.get('id')
        getfn = request.form.get('fn')
        getmn = ''
        getln = request.form.get('ln')
        getphone = request.form.get('phone')
        author = Author(id=getid, Fname=getfn, Mname=getmn, Lname=getln, phone_num=getphone)
        db.session.add(author)
        flash(f'The author {getfn} {getmn} {getln} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addauthor'))
    return render_template('books/addpublisher.html', authorss='authorss', publishers=publishers(), categories=categories(), authors=authors())

@app.route('/updateauthor/<int:id>', methods=['GET', 'POST'])
def updateauthor(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updateauthor = db.session.query(Author).filter_by(id=id).first_or_404()
    getfn = request.form.get('fn')
    getmn = ''
    getln = request.form.get('ln')
    getphone = request.form.get('phone')
    if request.method == 'POST':
        updateauthor.Fname = getfn
        updateauthor.Mname = getmn
        updateauthor.Lname = getln
        updateauthor.phone_num = getphone
        flash('Your author has been updated', 'success')
        db.session.commit()
        return redirect(url_for('authors'))
        
    return render_template('books/updatepublisher.html', title='Update author page', updateauthor=updateauthor, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/deleteauthor/<int:id>', methods=['POST'])
def deleteauthor(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    author = db.session.query(Author).filter_by(id=id).first_or_404()
    if request.method == 'POST':
        db.session.delete(author)
        flash(f'The author {author.Lname} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('authors'))
    flash(f'The author {author.Lname} can\'t be deleted', 'warning')
    return redirect(url_for('authors'))

@app.route('/discount/<int:id>')
def get_discount(id):
    page = request.args.get('page', 1, type=int)
    discountname = db.session.query(Discount).filter_by(id=id).first_or_404().name
    pbydiscount = db.session.query(Book).join(Book_discount, (Book.ISBN==Book_discount.book_id)).filter_by(discount_id=id).paginate(page=page, per_page=3)
    author_write_book = dict()
    book_belongs_to_category = dict()
    book_discount = dict()
    for book in pbydiscount.items:
        squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
        author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
        squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
        category = db.session.query(Category).filter(Category.name.in_(squery)).all()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()
        author_write_book[book.ISBN] = author
        book_belongs_to_category[book.ISBN] = category
        book_discount[book.ISBN] = [int(discount[0]*100), book.price*(1 - discount[0])] if discount[0] else [0, book.price]
    return render_template('books/index.html', books=pbydiscount, title=discountname, author_write_book=author_write_book, book_belongs_to_category=book_belongs_to_category, book_discount=book_discount, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/adddiscount', methods=['GET', 'POST'])
def adddiscount():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getid = request.form.get('id')
        getname = request.form.get('name')
        getvalue = request.form.get('value')
        discount = Discount(id=getid, name=getname, value=float(getvalue))
        db.session.add(discount)
        flash(f'The discount {getname} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('adddiscount'))
    return render_template('books/addpublisher.html', discountss='discountss', publishers=publishers(), categories=categories(), authors=authors())

@app.route('/updatediscount/<int:id>', methods=['GET', 'POST'])
def updatediscount(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updatediscount = db.session.query(Discount).filter_by(id=id).first_or_404()
    getfn = request.form.get('fn')
    getmn = ''
    getln = request.form.get('ln')
    getphone = request.form.get('phone')
    if request.method == 'POST':
        updatediscount.Fname = getfn
        updatediscount.Mname = getmn
        updatediscount.Lname = getln
        updatediscount.phone_num = getphone
        flash('Your discount has been updated', 'success')
        db.session.commit()
        return redirect(url_for('discounts'))
        
    return render_template('books/updatepublisher.html', title='Update discount page', updatediscount=updatediscount, publishers=publishers(), categories=categories(), authors=authors())

@app.route('/deletediscount/<int:id>', methods=['POST'])
def deletediscount(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    discount = db.session.query(Discount).filter_by(id=id).first_or_404()
    if request.method == 'POST':
        book_discount = db.session.query(Book_discount).filter_by(discount_id=id).all()
        for d in book_discount:
            db.session.delete(d)
        db.session.delete(discount)
        flash(f'The discount {discount.name} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('discounts'))
    flash(f'The discount {discount.name} can\'t be deleted', 'warning')
    return redirect(url_for('discounts'))

@app.route('/book/<string:isbn>')
def single_book(isbn):
    book = db.session.query(Book).filter_by(ISBN=isbn).first_or_404()
    squery = db.session.query(Author_write_book.Aphone_num).filter_by(ISBN=book.ISBN).subquery()
    author = db.session.query(Author).filter(Author.phone_num.in_(squery)).all()
    squery = db.session.query(Book_belongs_to_category.category_name).filter_by(ISBN=book.ISBN).subquery()
    category = db.session.query(Category).filter(Category.name.in_(squery)).all()
    squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
    discountmax = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()[0]
    discountprice = book.price * (1 - (discountmax if discountmax else 0))
    discount = db.session.query(Discount).filter_by(value=discountmax).first_or_404() if discountmax else None
    pid = db.session.query(Publisher).filter_by(name=book.Pname).first_or_404().id
    return render_template('books/single_book.html', book=book, author=author, category=category, discountprice=discountprice, pid=pid, discount=discount, publishers=publishers(), categories=categories(), authors=authors(), title=book.title)

@app.route('/addbook', methods=['POST', 'GET'])
def addbook():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = db.session.query(Publisher).all()
    categories = db.session.query(Category).all()
    authors = db.session.query(Author).all()
    discounts = db.session.query(Discount).all()
    form = Addbook(request.form)
    if request.method == 'POST':
        isbn = form.isbn.data
        title = form.title.data
        edition = form.edition.data
        publish_date = form.publish_date.data
        price = form.price.data
        stock = form.stock.data
        sales_amount = form.sales_amount.data
        shortdesc = form.shortdesc.data
        longdesc = form.longdesc.data
        author = request.form.getlist('author')
        category = request.form.getlist('category')
        publisher = request.form.get('publisher')
        discount = request.form.getlist('discount')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        
        addpro = Book(title=title, price=price, stock=stock, shortdesc=shortdesc,
                      Pname=publisher, image_1=image_1, image_2=image_2, image_3=image_3, edition=edition,
                      ISBN=isbn, publish_date=publish_date, sales_amount=sales_amount, longdesc=longdesc)

        db.session.add(addpro)
        
        for phone in author:
            add_auth_book = Author_write_book(Aphone_num=phone, ISBN=isbn)
            db.session.add(add_auth_book)
            
        for name in category:
            add_cate_book = Book_belongs_to_category(category_name=name, ISBN=isbn)
            db.session.add(add_cate_book)
            
        for id in discount:
            add_book_discount = Book_discount(discount_id=int(id), book_id=isbn)
            db.session.add(add_book_discount)
        
        flash(f'The book {title} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('books/addbook.html', title='Add Book page', form=form, publishers=publishers, categories=categories, authors=authors, discounts=discounts)

@app.route('/updatebook/<string:isbn>', methods=['GET', 'POST'])
def updatebook(isbn):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = db.session.query(Publisher).all()
    categories = db.session.query(Category).all()
    authors = db.session.query(Author).all()
    discounts = db.session.query(Discount).all()
    book = db.session.query(Book).filter_by(ISBN=isbn).first_or_404()
    form = Addbook(request.form)
    # author = request.form.getlist('author')
    # publisher = request.form.get('publisher')
    # category = request.form.getlist('category')
    discount = [int(i) for i in request.form.getlist('discount')]
    # old_discount = db.session.query(Book_discount).with_entities(Book_discount.discount_id).filter_by(book_id=isbn).all() multiple entities use this
    old_discount = [i[0] for i in db.session.query(Book_discount.discount_id).filter_by(book_id=isbn).all()]
    
    if request.method == 'POST':
        book.ISBN = form.isbn.data
        book.title = form.title.data
        book.edition = form.edition.data
        book.publish_date = form.publish_date.data
        book.price = form.price.data
        author = request.form.getlist('author')
        category = request.form.getlist('category')
        book.stock = form.stock.data
        book.sales_amount = form.sales_amount.data
        book.shortdesc = form.shortdesc.data
        book.longdesc = form.longdesc.data
        
        for phone in author:
            add_auth_book = Author_write_book(Aphone_num=phone, ISBN=isbn)
            db.session.add(add_auth_book)
            
        for name in category:
            add_cate_book = Book_belongs_to_category(category_name=name, ISBN=isbn)
            db.session.add(add_cate_book)
        
        for id in old_discount:
            if id not in discount and id != 0:
                deldiscount = db.session.query(Discount).filter_by(id=id).first_or_404()
                db.session.delete(deldiscount)
        
        for id in discount:
            if id not in old_discount and id != 0:
                add_book_discount = Book_discount(discount_id=id, book_id=isbn)
                db.session.add(add_book_discount)
        
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_1))
                book.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
            except:
                book.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_2))
                book.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
            except:
                book.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_3))
                book.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
            except:
                book.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
                 
        db.session.commit()
        flash('Your book has been updated', 'success')
        return redirect(url_for('admin'))
        
    
    form.isbn.data = book.ISBN 
    form.title.data = book.title
    form.edition.data = book.edition
    form.publish_date.data = book.publish_date 
    form.price.data = book.price
    form.stock.data = book.stock
    form.sales_amount.data = book.sales_amount
    form.shortdesc.data = book.shortdesc
    form.longdesc.data = book.longdesc
    return render_template('books/updatebook.html', title='Update book page', 
                           form=form, discounts=discounts, old_discount=old_discount, publishers=publishers, categories=categories, authors=authors)
    
@app.route('/deletebook/<string:isbn>', methods=['POST'])
def deletebook(isbn):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    book = db.session.query(Book).filter_by(ISBN=isbn).first_or_404()
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_1))
            os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_2))
            os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_3))
        except Exception as e:
            print(e)
        db.session.delete(book)
        flash(f'The book {book.title} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f'The book {book.title} can\'t be deleted', 'warning')
    return redirect(url_for('admin'))
