from typing import Dict
from flask import redirect, request, url_for, render_template, flash, session, current_app
from sqlalchemy import func
from iob_shop import db, app, photos
from iob_shop.books import Book, Discount, Book_discount

def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/addtocart', methods=['POST'])
def AddToCart():
    try:
        book_isbn = request.form.get('book_isbn')
        quantity = request.form.get('quantity')
        book = db.session.query(Book).filter_by(ISBN=book_isbn).first()
        squery = db.session.query(Book_discount.discount_id).filter_by(book_id=book.ISBN).subquery()
        discount = db.session.query(func.max(Discount.value)).filter(Discount.id.in_(squery)).first_or_404()[0]
        discountmax = discount if discount else 0
        discountprice = book.price * (1 - discountmax)
        if book_isbn and quantity and request.method == 'POST':
            DictItems = {book_isbn:{'title':book.title, 'price':book.price, 'quantity':quantity, 'discountmax':discountmax, 'discountprice':discountprice,'image':book.image_1}}
            
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if book_isbn in session['Shoppingcart']:
                    print('This book in already in your cart')
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
    
@app.route('/carts')
def get_cart():
    if 'Shoppingcart' not in session:
        try:
            return redirect(request.referrer)
        except:
            return redirect(url_for('home'))
    grandtotal = 0
    for key, book in session['Shoppingcart'].items():
        grandtotal += float(book['discountprice']) * float(book['quantity'])
    return render_template('books/carts.html', title='Cart', grandtotal=grandtotal)