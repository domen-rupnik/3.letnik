from base import Session
from models import *
from mail import send_mail
session = Session()

def check_reminders(id):
    produkti_uporabnika = session.query(Users_Products).filter_by(users_products_user_id=id).all()
    uporabnik = session.query(User.user_name).filter_by(user_id=id).first()[0]
    mail = session.query(User.user_email).filter_by(user_id=id).first()[0]
    for produkt in produkti_uporabnika:
        if produkt.users_products_sent_email:
            continue
        vse_trgovine = session.query(Products_Shop).filter_by(product_shop_product_id=produkt.users_products_product_id).all()
        spodnja = produkt.users_products_lower_reminder
        zgornja = produkt.users_products_upper_reminder
        ime = session.query(Product.product_name).filter_by(product_id=produkt.users_products_product_id).first()[0]
        je_l = False
        je_u = False
        if not spodnja and not zgornja:
            produkt.users_products_upper_condition = 0
            produkt.users_products_lower_condition = 0
            session.commit()
            continue
        najnizja = 1000000000
        for trgovina in vse_trgovine:
            if spodnja and trgovina.product_shop_price <= spodnja:
                # Pošljemo mail
                tema = "Cena opazovanega produkta je padla pod željeno ceno!"
                sporocilo = "Pozdravljen " + str(uporabnik) + ",\n\n v trgovini " + str(
                    trgovina.product_shop_shop_name) + ", je cena izdelka (" + str(
                    trgovina.product_shop_price) + "€), ki ste ga opazovali padla pod željeno ceno (" + str(
                    spodnja) + "€)." + "\nIzdelek najdete na povezavi: " + str(
                    trgovina.product_shop_url) + "\n\n\nLep pozdrav,\nEkipa TPO"
                send_mail(mail, tema, sporocilo)
                produkt.users_products_sent_email = 1
                session.commit()
                je_l = True
            if najnizja > trgovina.product_shop_price:
                najnizja = trgovina.product_shop_price
        if zgornja and najnizja > zgornja:
            # Pošljemo mail
            tema = "Cena opazovanega produkta se je dvignila nad željeno ceno!"
            sporocilo = "Pozdravljen " + str(uporabnik) + ",\n\nzaznali smo, da se je cena opazovanega izdelka" + ime + " (" + str(najnizja) + "€) dvignila nad željeno ceno (" + str(
                zgornja) + "€)!\n\n\nLep pozdrav,\nEkipa TPO"
            send_mail(mail, tema, sporocilo)
            produkt.users_products_sent_email = 1
            session.commit()
            je_u = True
        if je_l:
            produkt.users_products_lower_condition = 1
        else:
            produkt.users_products_lower_condition = 0
        if je_u:
            produkt.users_products_upper_condition = 1
        else:
            produkt.users_products_upper_condition = 0
        session.commit()
    return