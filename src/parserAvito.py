import json
import requests
import bs4
import datetime
import re
from collections import namedtuple
from datetime import timedelta

DataBlock = namedtuple('Block', 'title,desc,url,price,pubDate')


# класс для работы с данными как с именнованым tuple
class Block(DataBlock):
    def __str__(self):
        return f'name: {self.title},' \
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

    @staticmethod
    def parse_date(item: str):
        params = item.strip().split(' ')
        number = int(params[0])
        now = datetime.datetime.now()
        if params[1] == "минута" or params[1] == "минуты" or params[1] == "минут":
            time_delta = timedelta(minutes=number)
            return (now - time_delta).strftime('%Y-%d-%m %H:%M')
        elif params[1] == "час" or params[1] == "часов" or params[1] == "часа":
            time_delta = timedelta(hours=number)
            return (now - time_delta).strftime('%Y-%d-%m %H:%M')
        elif params[1] == "день" or params[1] == "дней" or params[1] == "дня":
            time_delta = timedelta(days=number)
            return (now - time_delta).strftime('%Y-%d-%m %H:%M')
        elif params[1] == "неделя" or params[1] == "недели" or params[1] == "неделю":
            time_delta = timedelta(weeks=number)
            return (now - time_delta).strftime('%Y-%d-%m %H:%M')
        dict_month = {
            "января": "01",
            "февраля": "02",
            "марта": "03",
            "апреля": "04",
            "мая": "05",
            "июня": "06",
            "июля": "07",
            "августа": "08",
            "сентебря": "09",
            "октября": "10",
            "ноября": "11",
            "декабря": "12"
        }
        date_time_str = str(now.year) + str(number) + "-" + dict_month.get(params[1]) + ":" + str(params[2])
        return datetime.datetime.strptime(date_time_str, "%Y-%d-%m\t%H:%M")

    def parse_block(self, item):
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
        # print("url: " + url)

        # 2.choose title announcement
        title_block = item.select_one("h3.title-root-395AQ.iva-item-title-1Rmmj.title-listRedesign-3RaU2."
                                      + "title-root_maxHeight-3obWc.text-text-1PdBw.text-size-s-1PUdo."
                                      + "text-bold-3R9dt")
        title = title_block.string.strip()
        # print("title: " + title)

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
        # print("price: " + price)

        # 4.pubDate
        pub_date_block = item.select_one("div.date-text-2jSvU.text-text-1PdBw.text-size-s-1PUdo."
                                         + "text-color-noaccent-bzEdI")
        pub_date = pub_date_block.string.strip()
        pub_date = self.parse_date(pub_date)
        # print("pubDate: " + pub_date)

        # 5.desc
        desc_block = item.select_one("div.iva-item-descriptionStep-3i2NN")
        if desc_block is None:
            desc = ""
        else:
            desc = desc_block.string.strip()
        # print("desc: " + desc)
        return Block(
            url=url,
            title=title,
            price=price,
            pubDate=pub_date,
            desc=desc
        )

    # in case when we want to change search param
    # user 0 - all, 1 - only individual, 2 - only company
    def get_page(self, page: int = None, name: str = None):
        name = name.replace(" ", "+")
        if name is None:
            print("Incorrect name")
            return None
        url = "https://www.avito.ru"
        if page and page > 1:
            url += "?p=" + str(page) + "&q=" + name + "&radius=0"
        else:
            url += "?q=" + name + "&radius=0"
        # print(url)
        return self.session.get(url).text

    def get_pagination_page(self, name: str):
        text = self.get_page(name=name)
        soup = bs4.BeautifulSoup(text, 'lxml')

        pages_block = soup.find_all('span', {'class': 'pagination-item-1WyVp'})
        pages_block = str(pages_block)
        pages_blocks = pages_block.split("</span>")
        return int(''.join(filter(lambda x: x.isdigit(), pages_blocks[-3][-3:])))

    def get_blocks(self, name: str, page: int):
        text = self.get_page(name=name, page=page)
        soup = bs4.BeautifulSoup(text, 'lxml')

        container = soup.select("div.iva-item-root-G3n7v.photo-slider-slider-3tEix.iva-item-list-2_PpT."
                                + "iva-item-redesign-1OBTh.items-item-1Hoqq.items-listItem-11orH.js-catalog-item-enum")
        ans = list()
        for item in container:
            ans.append(self.parse_block(item))
        return ans

    def parse(self, name: str):
        # pages = self.get_pagination_page(name=name)
        pages = 1
        objects = list()
        for i in range(pages):
            objects_last = self.get_blocks(name=name, page=i)
            for block in objects_last:
                objects.append(block)
        return objects
