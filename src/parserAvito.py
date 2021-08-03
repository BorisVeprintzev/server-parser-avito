import json
import requests
import bs4
import datetime
import time
from collections import namedtuple

DataBlock = namedtuple('Block', 'title,desc,url,price,pubDate')


# класс для работы с данными как с именнованым tuple
class Block(DataBlock):
    def __str__(self):
        return f'name: {self.title},' \
               f'\tdesc: {self.desc},' \
               f'\turl: {self.url},' \
               f'\tprice: {self.price},' \
               f'\tpubDate{self.pubDate}'

    def to_json(self):
        dict = {
            'title': self.title,
            'desc': self.desc,
            'url': self.url,
            'price': self.price,
            'pubDate': self.pubDate,
        }
        return json.dumps(dict)


class AvitoParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/92.0.4515.107 Safari/537.36',
            'Accept-Language': 'ru',
        }

    def parse_day(self, item: str):
        params = item.strip().split(' ')
        params[0:] = int(params[0])
        if params[1] is "минута" or "минуты" or "минут":



    @staticmethod
    def parse_block(item):
        # 1.choose Url to announcement
        url_block = item.select_one("a.link-link-39EVK.link-design-default-2sPEv."
                                    + "title-root-395AQ.iva-item-title-1Rmmj.title-listRedesign-3RaU2."
                                    + "title-root_maxHeight-3obWc")
        if item is None:
            print("Item empty")
            return None
        href = None
        if url_block is None:
            print("not found href")
        else:
            href = url_block.get("href")
        if href:
            url = "https://www.avito.ru" + href
        else:
            url = None
        print("url: " + url)

        # 2.choose title announcement
        title_block = item.select_one("h3.title-root-395AQ.iva-item-title-1Rmmj.title-listRedesign-3RaU2."
                                      + "title-root_maxHeight-3obWc.text-text-1PdBw.text-size-s-1PUdo."
                                      + "text-bold-3R9dt")
        title = title_block.string.strip()
        print("title: " + title)

        # 3.price
        price_block = item.select_one("span.price-price-32bra span")
        price_block = price_block.get_text('\n')
        price_block = list(filter(None, map(lambda i: i.strip(), price_block.split('\n'))))
        if len(price_block) is 2:
            price = price_block[0]
        else:
            price = 0
        if price_block is None:
            print("Price None")
        print("price: " + price)

        # 4.pubDate
        pub_date_block = item.select_one("div.date-text-2jSvU.text-text-1PdBw.text-size-s-1PUdo."
                                         + "text-color-noaccent-bzEdI")
        pub_date = pub_date_block.string.strip()
        print("pubDate: " + pub_date)

        desc_block = item.select_one("div.iva-item-descriptionStep-3i2NN")
        if desc_block is None:
            desc = ""
        else:
            desc = desc_block.string.strip()
        print("desc: " + desc)

    # in case when we want to change search param
    # user 0 - all, 1 - only individual, 2 - only company
    def get_page(self, page: int = None, user: int = 0, name: str = None):
        name = name.replace(" ", "+")
        if name is None:
            print("Incorrect name")
            return None
        url = "https://www.avito.ru"
        if page and page > 1:
            url += "?p=" + str(page) + "&q=" + name + "&radius=0"
        else:
            url += "?q=" + name + "&radius=0"
        print(url)
        return self.session.get(url).text

    def get_blocks(self, name: str = ""):
        text = self.get_page(name=name)
        soup = bs4.BeautifulSoup(text, 'lxml')

        container = soup.select("div.iva-item-root-G3n7v.photo-slider-slider-3tEix.iva-item-list-2_PpT."
                                + "iva-item-redesign-1OBTh.items-item-1Hoqq.items-listItem-11orH.js-catalog-item-enum")
        i = 0
        for item in container:
            print("number", i)
            i += 1
            self.parse_block(item)
