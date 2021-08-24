from bs4 import BeautifulSoup
import requests
import sqlite3
import time

class Scrapp:
    def __init__(self):
        self.page_check = "https://gratka.pl/motoryzacja/osobowe"
    def get_pages(self):
        r = requests.get(self.page_check)
        bs = BeautifulSoup(r.content, "lxml")
        return bs

    def sql(self):
        db = sqlite3.connect('gratka.db')
        cursor = db.cursor()
        #cursor.execute('''CREATE TABLE offers (title TEXT, price REAL, location TEXT, last_update TEXT, features TEXT, features2 TEXT, features3 TEXT, features4 TEXT, features5 TEXT, features6 TEXT, href TEXT)''')
        #db.commit()
        return cursor, db

    def run(self):
        con = self.get_pages()
        cur, com = self.sql()
        features_list = []
        product_list_elem = con.find_all("article", {"class": "teaserUnified teaserUnified--isNotEstate"})
        for i, cars in enumerate(product_list_elem):
            i += 1
            print("-" * 100)
            print("PRACUJE NAD OFERTA: ", i )
            time.sleep(0.1)
            offer_title = cars.find("a", {"class": "teaserUnified__anchor"}).get_text()
            offer_price = cars.find("p", {"class": "teaserUnified__price"}).get_text().strip()
            offer_href = cars["data-href"]
            offer_features = cars.find_all("li", {"class": "teaserUnified__listItem"})
            offer_location = cars.find("span", {"class" : "teaserUnified__location"}).get_text().strip().replace("                                         ","")
            offer_update = cars.find("li", {"class" : "teaserUnified__info"}).get_text()

            print(offer_title)
            print(offer_href)
            print(offer_price)
            print(offer_location)
            print(offer_update)

            for features in offer_features:
                features_list.append(features.get_text())
            print(features_list)
            #cur.execute('INSERT INTO offers VALUES (?,?,?,?,?,?,?,?,?,?,?)', (offer_title, offer_price, offer_location, offer_update, *features_list, offer_href))
            features_list.clear()
            #com.commit()
        print("-" * 100)
        com.close()


s = Scrapp()
#s.sql()
s.run()
