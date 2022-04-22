from crypt import methods
from unicodedata import category
from click import File
from flask import redirect, request, url_for, render_template, flash, session, current_app
from iob_shop import db, app, photos
from iob_shop.admin.routes import publishers
from .models import Publisher, Category, Author, Product
from .forms import Addproduct
import secrets, os

@app.route('/')
@app.route('/home')
def home():
    products = Product.query.filter(Product.stock > 0)
    publishers = Publisher.query.join(Product, (Publisher.id==Product.publisher_id)).all()
    categories = Category.query.join(Product, (Category.id==Product.category_id)).all()
    authors = Author.query.join(Product, (Author.id==Product.author_id)).all()
    return render_template('products/index.html', products=products, publishers=publishers, categories=categories, authors=authors, title='Home')

@app.route('/publisher/<int:id>')
def get_publisher(id):
    pbypublisher = Product.query.filter_by(publisher_id=id)
    return render_template('products/index.html', products=pbypublisher, title=Publisher.query.get_or_404(id).name)

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
    return render_template('products/addpublisher.html', publisherss='publisherss')

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
        
    return render_template('products/updatepublisher.html', title='Update publisher page', updatepublisher=updatepublisher)

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
    pbycategory = Product.query.filter_by(category_id=id)
    return render_template('products/index.html', products=pbycategory, title=Category.query.get_or_404(id).name)

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
    return render_template('products/addpublisher.html')

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
    
    return render_template('products/updatepublisher.html', title="Update category page", updatecategory=updatecategory)

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
    pbyauthor = Product.query.filter_by(author_id=id)
    return render_template('products/index.html', products=pbyauthor, title=Author.query.get_or_404(id).name)

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
    return render_template('products/addpublisher.html', authorss='authorss')

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
        
    return render_template('products/updatepublisher.html', title='Update author page', updateauthor=updateauthor)

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


@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = Publisher.query.all()
    categories = Category.query.all()
    authors = Author.query.all()
    form = Addproduct(request.form)
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
        
        addpro = Product(name=name, price=price, discount=discount, stock=stock, author_id=author, desc=desc, publisher_id=publisher, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addpro)
        flash(f'The product {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', title='Add Product page', form=form, publishers=publishers, categories=categories, authors=authors)

@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    publishers = Publisher.query.all()
    categories = Category.query.all()
    authors = Author.query.all()
    product = Product.query.get_or_404(id)
    form = Addproduct(request.form)
    publisher = request.form.get('publisher')
    category = request.form.get('category')
    author = request.form.get('author')
    
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.publisher_id = publisher
        product.category_id = category
        product.author_id = author
        product.desc = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/product/' + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/product/' + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/product/' + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
                 
        db.session.commit()
        flash('Your product has been updated', 'success')
        return redirect(url_for('admin'))
        
    
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.description.data = product.desc
    return render_template('products/updateproduct.html', title='Update product page', 
                           form=form, publishers=publishers, categories=categories, authors=authors,product=product)
    
@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, 'static/images/product/' + product.image_1))
            os.unlink(os.path.join(current_app.root_path, 'static/images/product/' + product.image_2))
            os.unlink(os.path.join(current_app.root_path, 'static/images/product/' + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        flash(f'The product {product.name} was deleted from your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f'The product {product.name} can\'t be deleted', 'warning')
    return redirect(url_for('admin'))