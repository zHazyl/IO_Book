from unicodedata import category
from click import File
from flask import redirect, request, url_for, render_template, flash, session, current_app
from iob_shop import db, app, photos
from .models import Publisher, Category, Product
from .forms import Addproduct
import secrets, os
from PIL import Image 


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
    return render_template('products/addpublisher.html', publishers='publishers')

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


@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    publishers = Publisher.query.all()
    categories = Category.query.all()
    form = Addproduct(request.form)
    if request.method == 'POST':
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        format = form.format.data
        desc = form.description.data
        publisher = request.form.get('publisher')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        
        addpro = Product(name=name, price=price, discount=discount, stock=stock, format=format, desc=desc, publisher_id=publisher, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addpro)
        flash(f'The product {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', title='Add Product page', form=form, publishers=publishers, categories=categories)

@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    publishers = Publisher.query.all()
    categories = Category.query.all()
    product = Product.query.get_or_404(id)
    form = Addproduct(request.form)
    publisher = request.form.get('publisher')
    category = request.form.get('category')
    
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.publisher_id = publisher
        product.category_id = category
        product.format = form.format.data
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
    form.format.data = product.format
    form.description.data = product.desc
    return render_template('products/updateproduct.html', title='Update product page', 
                           form=form, publishers=publishers, categories=categories, product=product)