from base import Session
from models import *
from flask import Flask, jsonify, request, redirect, url_for, make_response
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
from sqlalchemy import func
from scraper import scraper, primerjajIzdelka
from checkReminders import check_reminders
from mail import send_mail

session = Session()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "pricemonitoringappsecretkey"
api = Api(app)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})


# Dekorator za pregled tokena
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({"Result": "Token is missing"}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = session.query(User).filter_by(user_id=data['public_id']).first()
        except:
            session.commit()
            return jsonify({"Result": "Token is invalid"}), 401
        session.commit()
        return f(current_user, *args, **kwargs)

    return decorated

# Registracija uporabnika
@app.route('/sign_up', methods=['POST'])

def sign_up():
    data = request.json
    name = (data['name'] if 'name' in data else None)
    surname = (data['surname'] if 'surname' in data else None)
    email = (data['email'] if 'email' in data else None)
    password = (data['password'] if 'password' in data else None)
    # Manjkajoči podatki
    if not name or not surname or not password or not email:
        session.commit()
        return jsonify({'Result': 'Missing data'})
    # Uporabnik že obstaja
    obstaja_uporabnik = session.query(User.user_email).filter_by(user_email=email).scalar() is not None
    if obstaja_uporabnik:
        session.commit()
        return jsonify({'Result': 'User already exists'})

    max_id = session.query(func.max(User.user_id)).scalar()
    if not max_id:
        max_id = 500
    new_user = User(user_id=max_id + 1,
                    user_name=name,
                    user_surname=surname,
                    user_email=email,
                    user_password=password.upper())
    session.add(new_user)
    session.commit()
    tema = "Uspešna registracija"
    sporocilo = "Pozdravljen {}," \
                "\n\nvaša registracija v sistem pregledovanja cen artiklov je uspešna." \
                "\n\nLep pozdrav," \
                "\nEkipa TPO".format(name)
    send_mail(email, tema, sporocilo)
    return jsonify({'Result': 'Registered successfully'})


# Prijava uporabnika
@app.route('/sign_in', methods=['POST'])

def sign_in():
    data = request.json
    email = (data['email'] if 'email' in data else None)
    password = (data['password'] if 'password' in data else None)

    user = session.query(User).filter_by(user_email=email).first()
    # Če uporabnik ne obstaja
    if not user:
        session.commit()
        return jsonify({'Result': 'User does not exist'})
    # Če uporabnik obstaja in je nepravilno geslo
    if user.user_password.upper() != password.upper():
        session.commit()
        return jsonify({'Result': 'Wrong password'})
    token = jwt.encode(
        {'public_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'])
    session.commit()
    return jsonify({'Result': 'Logged in successfully',
                    'name': user.user_name,
                    'surname': user.user_surname,
                    'token': token.decode('UTF-8')})


@app.route('/add_item', methods=['POST'])
@token_required
def add_item(current_user):
    data = request.json
    url = (data['url'] if 'url' in data else None)
    if not url:
        return jsonify({'Result': 'No url'})
    podatki = scraper(url)
    ime_izdelka = podatki['Ime']
    # Pogledamo če se kakšno ime ujema
    vsi_izdelki = session.query(Product).all()
    izdelek_obstaja = False
    for ime in vsi_izdelki:
        if primerjajIzdelka(ime.product_name, ime_izdelka):
            izdelek_obstaja = True
            ime_izdelka = ime.product_name
            break
    if izdelek_obstaja:
        obstojec_izdelek = session.query(Product).filter_by(product_name=ime_izdelka).first()
        # Če uporabnik že ima izdelek
        if session.query(Users_Products.users_products_user_id).filter_by(
                users_products_user_id=current_user.user_id,
                users_products_product_id=obstojec_izdelek.product_id).scalar() is None:
            nov_uporabnikov_izdelek = Users_Products(users_products_user_id=current_user.user_id,
                                                     users_products_product_id=obstojec_izdelek.product_id)
            session.add(nov_uporabnikov_izdelek)
            session.commit()

        trgovina = podatki['Trgovina']
        # Če je že ta trgovina za ta izdelek
        if session.query(Products_Shop).filter_by(product_shop_product_id=obstojec_izdelek.product_id,
                                                  product_shop_shop_name=trgovina).first() is not None:
            session.commit()
            return jsonify({'Result': 'Product added successfully'})
        # Če ni še te trgovine za ta izdelek
        else:
            max_id = session.query(func.max(Products_Shop.product_shop_id)).scalar()
            if not max_id:
                max_id = 999
            max_id += 1
            nova_trgovina = Products_Shop(product_shop_id=max_id, product_shop_product_id=obstojec_izdelek.product_id,
                                          product_shop_shop_name=trgovina, product_shop_url=url,
                                          product_shop_discount=podatki['Popust'],
                                          product_shop_price=podatki['Trenutna cena'])

            session.add(nova_trgovina)
            session.commit()
            max_id2 = session.query(func.max(Price.price_id)).scalar()
            if not max_id2:
                max_id2 = 999
            max_id2 += 1
            datum = datetime.datetime.today().strftime('%d.%m.%Y')
            nova_cena = Price(price_id=max_id2, price_price=podatki['Trenutna cena'], price_date=datum,
                              price_product_shop_id=max_id)
            session.add(nova_cena)
            session.commit()
            return jsonify({'Result': 'Product added successfully'})
    # Če izdelek ne obstaja
    else:
        # Najprej dodamo izdelek
        max_id = session.query(func.max(Product.product_id)).scalar()
        if not max_id:
            max_id = 999
        max_id += 1
        nov_izdelek = Product(product_id=max_id, product_name=ime_izdelka, product_image=podatki['Slika'])
        session.add(nov_izdelek)
        session.commit()
        # Naredimo novo trgovino za izdelek
        max_id2 = session.query(func.max(Products_Shop.product_shop_id)).scalar()
        if not max_id2:
            max_id2 = 999
        max_id2 += 1
        nova_trgovina = Products_Shop(product_shop_id=max_id2, product_shop_product_id=max_id, product_shop_url=url,
                                      product_shop_shop_name=podatki['Trgovina'],
                                      product_shop_discount=podatki['Popust'],
                                      product_shop_price=podatki['Trenutna cena'])
        session.add(nova_trgovina)
        session.commit()
        # Dodamo novo ceno
        max_id = session.query(func.max(Price.price_id)).scalar()
        if not max_id:
            max_id = 999
        max_id += 1
        datum = datetime.datetime.today().strftime('%d.%m.%Y')
        nova_cena = Price(price_id=max_id, price_product_shop_id=max_id2, price_date=datum,
                          price_price=podatki['Trenutna cena'])
        session.add(nova_cena)
        session.commit()
        # Uporabniku dodamo izdelek
        max_id = session.query(func.max(Product.product_id)).scalar()
        nov_uporabnikov_izdelek = Users_Products(users_products_user_id=current_user.user_id,
                                                 users_products_product_id=max_id)
        session.add(nov_uporabnikov_izdelek)
        session.commit()
        return jsonify({'Result': 'Product added successfully'})


# Vsi artikli uporabnika
@app.route("/user_items", methods=['GET'])
@token_required
def user_items(current_user):
    artikli = session.query(Users_Products).filter_by(users_products_user_id=current_user.user_id).all()
    output = []
    if not artikli:
        session.commit()
        return jsonify({'Result': 'No products'})
    for artikel in artikli:
        product_data = {}
        product = session.query(Product).filter_by(product_id=artikel.users_products_product_id).first()
        product_data['id'] = product.product_id
        product_data['name'] = product.product_name
        product_data['image'] = product.product_image
        vse_trgovine = session.query(Products_Shop).filter_by(product_shop_product_id=product.product_id).all()
        min_cena = 100000000000
        for produkti in vse_trgovine:
            if produkti.product_shop_price < min_cena:
                min_cena = produkti.product_shop_price
        product_data['price'] = float(min_cena)
        pogoj = False
        if session.query(Users_Products.users_products_lower_condition).filter_by(
                users_products_user_id=current_user.user_id, users_products_product_id=product.product_id).first()[0] or session.query(
            Users_Products.users_products_upper_condition).filter_by(users_products_user_id=current_user.user_id,
                                                                     users_products_product_id=product.product_id).first()[0]:
            pogoj = True
        spodnja = \
            session.query(Users_Products.users_products_lower_reminder).filter_by(
                users_products_user_id=current_user.user_id,
                users_products_product_id=product.product_id).first()[0]
        zgornja = \
            session.query(Users_Products.users_products_upper_reminder).filter_by(
                users_products_user_id=current_user.user_id,
                users_products_product_id=product.product_id).first()[0]
        if zgornja:
            zgornja = float(zgornja)
        if spodnja:
            spodnja = float(spodnja)
        product_data['condition'] = pogoj
        product_data['lower'] = spodnja
        product_data['upper'] = zgornja
        output.append(product_data)
    session.commit()
    return jsonify({'Products': output})


# 10 artiklov za domači zaslon
@app.route('/home_items', methods=['GET'])
def home_items():
    stmt = session.query(Product).order_by(func.random()).all()
    if len(stmt) > 10:
        stmt = stmt[:10]
    output = []
    for product in stmt:
        product_data = {}
        product_data['id'] = product.product_id
        product_data['name'] = product.product_name
        product_data['image'] = product.product_image
        vse_trgovine = session.query(Products_Shop).filter_by(product_shop_product_id=product.product_id).all()
        min_cena = 100000000000
        for produkti in vse_trgovine:
            if produkti.product_shop_price < min_cena:
                min_cena = produkti.product_shop_price
        product_data['price'] = float(min_cena)
        output.append(product_data)
    session.commit()
    return jsonify({'Products': output})


# Podrobnosti izdelka
@app.route('/product', methods=['POST'])
def product():
    token = None
    id = request.json['id']
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
    if not token:
        return product_logged_out(id)
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
        current_user = session.query(User).filter_by(user_id=data['public_id']).first()
        return product_logged_in(current_user, id)
    except:
        return

# Podrobnosti produkta, če je uporabnik prijavljen
def product_logged_in(current_user, id):
    izdelek = session.query(Product).filter_by(product_id=id).first()
    ime = izdelek.product_name
    slika = izdelek.product_image
    vse_trgovine = session.query(Products_Shop).filter_by(product_shop_product_id=id).all()
    output = {}
    min_cena = 100000000000
    for produkti in vse_trgovine:
        if produkti.product_shop_price < min_cena:
            min_cena = produkti.product_shop_price
        cene = session.query(Price).filter_by(price_product_shop_id=produkti.product_shop_id).all()
        out = []
        for cena in cene:
            out.append({str(cena.price_date): float(cena.price_price)})
        output[produkti.product_shop_shop_name] = {'url': produkti.product_shop_url, 'prices': out}
    session.commit()
    if not session.query(Users_Products).filter_by(users_products_user_id=current_user.user_id, users_products_product_id=id).first():
        return jsonify(
            {'id': id, 'name': ime, 'image': slika, 'price': float(min_cena), 'prices_data': output})
    pogoj = False
    if session.query(Users_Products.users_products_lower_condition).filter_by(
            users_products_user_id=current_user.user_id, users_products_product_id=id).first()[0] or session.query(
            Users_Products.users_products_upper_condition).filter_by(users_products_user_id=current_user.user_id,
                                                                     users_products_product_id=id).first()[0]:
        pogoj = True
    spodnja = \
    session.query(Users_Products.users_products_lower_reminder).filter_by(users_products_user_id=current_user.user_id,
                                                                          users_products_product_id=id).first()[0]
    zgornja = \
    session.query(Users_Products.users_products_upper_reminder).filter_by(users_products_user_id=current_user.user_id,
                                                                          users_products_product_id=id).first()[0]
    if zgornja:
        zgornja = float(zgornja)
    if spodnja:
        spodnja = float(spodnja)
    return jsonify({'id': id, 'name': ime, 'image': slika, 'price': float(min_cena), 'prices_data': output, 'condition': pogoj, 'lower': spodnja, 'upper': zgornja})

# Podrobnosti izdelka brez prijave
def product_logged_out(id):
    izdelek = session.query(Product).filter_by(product_id=id).first()
    ime = izdelek.product_name
    slika = izdelek.product_image
    vse_trgovine = session.query(Products_Shop).filter_by(product_shop_product_id=id).all()
    output = {}
    min_cena = 100000000000
    for produkti in vse_trgovine:
        if produkti.product_shop_price < min_cena:
            min_cena = produkti.product_shop_price
        cene = session.query(Price).filter_by(price_product_shop_id=produkti.product_shop_id).all()
        out = []
        for cena in cene:
            out.append({str(cena.price_date): float(cena.price_price)})
        output[produkti.product_shop_shop_name] = {'url': produkti.product_shop_url, 'prices': out}
    session.commit()
    return jsonify({'id': id, 'name': ime, 'image': slika, 'price': float(min_cena), 'prices_data': output})

# Odstranitev izdelka
@app.route('/remove_product', methods=['POST'])
@token_required
def remove_product(current_user):
    data = request.json
    uporabnik = current_user.user_id
    izdelek = (data['id'] if 'id' in data else None)
    if not uporabnik or not izdelek:
        return jsonify({'Result': 'Missing data'})
    user = session.query(User).filter_by(user_id=uporabnik).first()
    product = session.query(Product).filter_by(product_id=izdelek).first()
    if not user:
        session.commit()
        return jsonify({'Result': 'No user'})
    if not product:
        session.commit()
        return jsonify({'Result': 'No product'})
    ima_izdelek = session.query(Users_Products).filter_by(users_products_user_id=uporabnik,
                                                 users_products_product_id=izdelek).first()
    if not ima_izdelek:
        session.commit()
        return jsonify({'Result': 'This product is not on users watchlist'})
    session.query(Users_Products).filter_by(users_products_user_id=uporabnik, users_products_product_id=izdelek).delete()
    session.commit()
    return jsonify({'Result': 'Product removed'})


# Posodabljanje cene izdelkov
@app.route('/update_products', methods=['GET'])
def update_products():
    vsi_izdelki = session.query(Products_Shop).all()
    datum = datetime.datetime.today().strftime('%d.%m.%Y')
    max_id = session.query(func.max(Price.price_id)).scalar()
    for izdelek in vsi_izdelki:
        try:
            podatki = scraper(izdelek.product_shop_url)
            max_id += 1
            nova_cena = Price(price_id=max_id, price_product_shop_id=izdelek.product_shop_id,
                              price_price=round(podatki['Trenutna cena'], 2), price_date=datum)
            session.add(nova_cena)
            session.commit()

        except:
            continue
    session.commit()
    uporabniki = session.query(User.user_id).all()
    for id in uporabniki:
        check_reminders(id[0])
    return jsonify({'Result': 'Product prices updated'})

# Nastavljanje opomnikov cen
@app.route('/conditions_product', methods=['POST'])
@token_required
def conditions_product(current_user):
    data = request.json
    id = (data['id'] if 'id' in data else None)
    spodnja = (data['spodnja'] if 'spodnja' in data else None)
    zgornja = (data['zgornja'] if 'zgornja' in data else None)

    if not id:
        return jsonify({'Result': 'Missing id'})
    if zgornja:
        zgornja = round(zgornja, 2)
    if spodnja:
        spodnja = round(spodnja, 2)
    if spodnja and zgornja and spodnja > zgornja:
        spodnja, zgornja = zgornja, spodnja
    user = session.query(Users_Products).filter_by(users_products_user_id=current_user.user_id,
                                                   users_products_product_id=id).first()
    user.users_products_lower_reminder = spodnja
    user.users_products_upper_reminder = zgornja
    user.users_products_sent_email = 0
    session.commit()
    check_reminders(current_user.user_id)
    return jsonify({'Result': 'Reminders set successfully'})


if __name__ == '__main__':
    # create_all()
    app.run(debug=True)

