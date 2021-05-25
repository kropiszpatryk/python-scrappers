import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
import sqlite3


class Scrapper:
    def __init__(self):
        self.page_checker_uri = 'https://www.morele.net/kategoria/monitory-523/,,,,,,,,0,,,,/1/'
        self.displays_uri = 'https://www.morele.net/kategoria/monitory-523/,,,,,,,,0,,,,/{}/'

    def get_page_count(self):
        r = requests.get(self.page_checker_uri)
        soup = BeautifulSoup(r.content, 'lxml')
        pagination_btn = soup.find_all('a', {"class": "pagination-btn"})[2]
        return int(pagination_btn['data-page'])

    def fetch_site_content(self, index):
        r = requests.get(self.displays_uri.format(index))  # dostep do content html
        return r.content

    def sql(self):
        db = sqlite3.connect('scrapping_db.db')
        cursor = db.cursor()
        #tworzenie kolumn, odkomeentowac tylko przy tworzeniu bazy
        #cursor.execute('''CREATE TABLE offers (tytul TEXT, cena REAL, href TEXT, czestotliwosc odswiezania TEXT, Podstawowe zlacza TEXT, Przekatna ekranu TEXT, Rozdzielczosc TEXT, Typ matrycy TEXT)''')
        #db.commit()
        return cursor, db

    def run(self):
        # przekazujemy content html i parsujemy go zeby móć go uzywac
        cur, com = self.sql()
        pages = self.get_page_count()
        features_list = []
        for i in range(pages + 1):
            print(' ======== STRONA', i +1, '========')
            soup = BeautifulSoup(self.fetch_site_content(i), 'lxml')
            # pobieramy wszystkie elementy które mają tag związany z tym ze są jakiś produktem
            product_list_elem = soup.find_all("div", {"class": "cat-product card"})

            # idziemy po wszystkich ogłoszeniach iterujac po nich
            for product in product_list_elem:
                base_uri = 'https://www.morele.net'
                product_link = product.find("a", {"class": "cat-product-image productLink"})
                product_title = product['data-product-name']
                product_price = str(product['data-product-price']) + " zł"
                product_href = base_uri + product_link['href']
                product_feature = product.find_all("div", {"class": "cat-product-feature"})

                for features in product_feature:
                    features_list.append(
                        features.get_text().strip().replace('\n', '').replace('Częstotliwość odświeżania:', '').replace(
                            'Podstawowe złącza:', '').replace('Przekątna ekranu', '').replace('Rozdzielczość:',
                                                                                              '').replace(
                            'Typ matrycy:', ''))

                print(features_list)

                print(product_title, product_price, product_href)
                print("============================================")
                cur.execute('INSERT INTO offers VALUES (?,?,?,?,?,?,?,?)',
                            (product_title, product_price, product_href, *features_list))
                com.commit()
                features_list.clear()

                # ZDJECIA!
                image_href = product_link.find("img", {"class": "product-image"})
                image_uri = None

                try:
                    image_uri = image_href.attrs['src']
                except:
                    image_uri = image_href.attrs['data-src']

                im = Image.open(requests.get(image_uri, stream=True).raw)

                #stworzyc folder jesli nie istnieje
                try:
                    os.mkdir(str(os.getcwd()) + "/" + str(i))
                except FileExistsError:
                    pass

                #zapisać w folderze o nazwie strony plik
                im.save("{}/".format(i) + str(product['data-product-name']).replace("/", "") + ".png")

s = Scrapper()
#s.sql() / odkomentowac przy tworzeniu bazy
s.run()
