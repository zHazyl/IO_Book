from typing import Dict
from flask import redirect, request, url_for, render_template, flash, session, current_app
from iob_shop import db, app, photos
from iob_shop.books import Book

def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/addtocart', methods=['POST'])
def AddToCart():
    try:
        book_id = request.form.get('book_id')
        quantity = request.form.get('quantity')
        book = Book.query.filter_by(id=book_id).first()
        if book_id and quantity and request.method == 'POST':
            DictItems = {book_id:{'name':book.name, 'price':book.price, 'discount':book.discount, 'quantity':quantity, 'image':book.image_1}}
            
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if book_id in session['Shoppingcart']:
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