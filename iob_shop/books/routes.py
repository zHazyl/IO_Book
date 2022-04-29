from crypt import methods
from unicodedata import category
from click import File
from flask import redirect, request, url_for, render_template, flash, session, current_app
from iob_shop import db, app, photos
from iob_shop.admin.routes import publishers
from .models import Publisher, Category, Author, Book
from .forms import Addbook
import secrets, os

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    books = Book.query.filter(Book.stock > 0).paginate(page=page, per_page=2)
    publishers = Publisher.query.join(Book, (Publisher.id==Book.publisher_id)).all()
    categories = Category.query.join(Book, (Category.id==Book.category_id)).all()
    authors = Author.query.join(Book, (Author.id==Book.author_id)).all()
    return render_template('books/index.html', books=books, publishers=publishers, categories=categories, authors=authors, title='Home')

@app.route('/publisher/<int:id>')
def get_publisher(id):
    page = request.args.get('page', 1, type=int)
    pbypublisher = Book.query.filter_by(publisher_id=id).paginate(page=page, per_page=3)
    return render_template('books/index.html', books=pbypublisher, title=Publisher.query.get_or_404(id).name)

@app.route('/addpublisher', methods=['GET', 'POST'])
def addpublisher():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getpublisher = request.form.get('publisher')
        publisher = Publisher(name=getpublisher)
        db.session.add(publisher)
        flash(f'The Publisher {getpublisher} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addpublisher'))
    return render_template('books/addpublisher.html', publisherss='publisherss')

@app.route('/updatepublisher/<int:id>', methods=['GET', 'POST'])
def updatepublisher(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updatepublisher = Publisher.query.get_or_404(id)
    publisher = request.form.get('publisher')
    if request.method == 'POST':
        updatepublisher.name = publisher
        flash('Your publisher has been updated', 'success')
        db.session.commit()
        return redirect(url_for('publishers'))
        
    return render_template('books/updatepublisher.html', title='Update publisher page', updatepublisher=updatepublisher)

@app.route('/deletepublisher/<int:id>', methods=['POST'])
def deletepublisher(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    publisher = Publisher.query.get_or_404(id)
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
    pbycategory = Book.query.filter_by(category_id=id).paginate(page=page, per_page=3)
    return render_template('books/index.html', books=pbycategory, title=Category.query.get_or_404(id).name)

@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The Category {getcategory} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcategory'))
    return render_template('books/addpublisher.html')

@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        updatecategory.name = category
        flash('Your category has been updated', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    
    return render_template('books/updatepublisher.html', title="Update category page", updatecategory=updatecategory)

@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    
    category = Category.query.get_or_404(id)
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
    pbyauthor = Book.query.filter_by(author_id=id).paginate(page=page, per_page=3)
    return render_template('books/index.html', books=pbyauthor, title=Author.query.get_or_404(id).name)

@app.route('/addauthor', methods=['GET', 'POST'])
def addauthor():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getauthor = request.form.get('author')
        author = Author(name=getauthor)
        db.session.add(author)
        flash(f'The author {getauthor} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addauthor'))
    return render_template('books/addpublisher.html', authorss='authorss')

@app.route('/updateauthor/<int:id>', methods=['GET', 'POST'])
def updateauthor(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    updateauthor = Author.query.get_or_404(id)
    author = request.form.get('author')
    if request.method == 'POST':
        updateauthor.name = author
        flash('Your author has been updated', 'success')
        db.session.commit()
        return redirect(url_for('authors'))
        
    return render_template('books/updatepublisher.html', title='Update author page', updateauthor=updateauthor)

@app.route('/deleteauthor/<int:id>', methods=['POST'])
def deleteauthor(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return render_template(url_for('login'))
    author = Author.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(author)
        flash(f'The author {author.name} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('authors'))
    flash(f'The author {author.name} can\'t be deleted', 'warning')
    return redirect(url_for('authors'))

@app.route('/book/<int:id>')
def single_book(id):
    book = Book.query.get_or_404(id)
    return render_template('books/single_book.html', book=book)

@app.route('/addbook', methods=['POST', 'GET'])
def addbook():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = Publisher.query.all()
    categories = Category.query.all()
    authors = Author.query.all()
    form = Addbook(request.form)
    if request.method == 'POST':
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        desc = form.description.data
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        
        addpro = Book(name=name, price=price, discount=discount, stock=stock, author_id=author, desc=desc, publisher_id=publisher, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addpro)
        flash(f'The book {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('books/addbook.html', title='Add Book page', form=form, publishers=publishers, categories=categories, authors=authors)

@app.route('/updatebook/<int:id>', methods=['GET', 'POST'])
def updatebook(id):
    publishers = Publisher.query.all()
    categories = Category.query.all()
    authors = Author.query.all()
    book = Book.query.get_or_404(id)
    form = Addbook(request.form)
    publisher = request.form.get('publisher')
    category = request.form.get('category')
    author = request.form.get('author')
    
    if request.method == 'POST':
        book.name = form.name.data
        book.price = form.price.data
        book.discount = form.discount.data
        book.stock = form.stock.data
        book.publisher_id = publisher
        book.category_id = category
        book.author_id = author
        book.desc = form.description.data
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
        
    
    form.name.data = book.name
    form.price.data = book.price
    form.discount.data = book.discount
    form.stock.data = book.stock
    form.description.data = book.desc
    return render_template('books/updatebook.html', title='Update book page', 
                           form=form, publishers=publishers, categories=categories, authors=authors,book=book)
    
@app.route('/deletebook/<int:id>', methods=['POST'])
def deletebook(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_1))
            os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_2))
            os.unlink(os.path.join(current_app.root_path, 'static/images/book/' + book.image_3))
        except Exception as e:
            print(e)
        db.session.delete(book)
        flash(f'The book {book.name} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f'The book {book.name} can\'t be deleted', 'warning')
    return redirect(url_for('admin'))