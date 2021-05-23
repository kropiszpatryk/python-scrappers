from bs4 import BeautifulSoup
import requests
import sqlite3
import time


class Scrapper:

    def __init__(self):
        self.page = "https://www.otomoto.pl/osobowe/bmw/seria-3/?search%5Bfilter_enum_generation%5D=gen-f30-2012"

    def get_pages(self):
        r = requests.get(self.page)
        bs = BeautifulSoup(r.content, "lxml")
        return bs

    def sql(self):
        db = sqlite3.connect('otomoto.db')
        cursor = db.cursor()
        #cursor.execute('''CREATE TABLE offers (title TEXT, price REAL, location TEXT, description TEXT, year TEXT, mileage TEXT, engine_capacity TEXT, fuel_type TEXT, href TEXT)''')
        #db.commit()
        return cursor, db

    def run_program(self):
        con = self.get_pages()
        cur, com = self.sql()
        product_list = con.find_all("div", {"class": "offers list"})
        features_list = []
        for prod in product_list:
            prod_spec = prod.find_all("div", {"class" : "offer-item__wrapper"})
            for i, spec in enumerate(prod_spec):
                product_href = spec.find("a", {"class" : "offer-title__link"})['href']
                product_title = spec.find("a", {"class" : "offer-title__link"})['title']
                product_price = spec.find("span", {"class" : "offer-price__number ds-price-number"}).get_text().strip().replace("PLN","")
                product_description = spec.find("h3",{"class" : "offer-item__subtitle ds-title-complement hidden-xs"}).get_text()
                product_location_city = spec.find("span", {"class" : "ds-location-city"}).get_text()
                product_location_region = spec.find("span", {"class": "ds-location-region"}).get_text()
                product_location = product_location_city + product_location_region
                product_features = spec.find_all("li", {"class": "ds-param"})
                for features in product_features:
                    features_list.append(features.get_text().strip().replace("km","").replace("cm3",""))
                print("-" * 100)

                print("Oferta: ", i)
                print(product_title)
                print(product_price)
                print(product_location)
                print(product_description)
                print(features_list)
                print(product_href)
                cur.execute('INSERT INTO offers VALUES (?,?,?,?,?,?,?,?,?)', (product_title, product_price, product_location, product_description, *features_list, product_href))
                com.commit()
                features_list.clear()
            print("-" * 100)
s = Scrapper()
#s.sql()
s.run_program()