import requests
import random
import json
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Host': 'steambuy.com',
    'Pragma': 'no-cache',
    'Referer': 'https://steambuy.com/catalog/',
    'X-Requested-With': 'XMLHttpRequest'
}

URL = 'https://steambuy.com/ajax/_get.php?rnd={}&offset={}&region_free=0&sort=cnt_sell' \
      '&sortMode=descendant&view=extended&a=getcat&q=&series=&izdatel=&currency=wmr&curr=&currMaxSumm[wmr]=3000' \
      '&currMaxSumm[wmz]=100&currMaxSumm[wme]=70&currMaxSumm[wmu]=1000&letter=&limit=0&page={}&minPrice=0' \
      '&maxPrice=9999&minDate=0&maxDate=0&deleted=0&no_price_range=0&records=20'

URl_API = 'http://steammachine.ru/api/good/?id_good={}&v=1&format=json'

URl_TEST = 'https://steambuy.com/steam/pillars-of-eternity-ii-deadfire-season-pass/'


def save_page(response_str, file_name='page.html'):
    with open(file_name, 'w', encoding='utf8') as html_file:
        html_file.write(response_str)


def save_json(data, file_name='data.json'):
    with open(file_name, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=True)


def get_json_from_catalog(offset, page):
    url = URL.format(random.random(), offset, page)
    response = requests.get(url, headers=HEADERS)
    return response.json()


def get_max_page():
    json_from_catalog = get_json_from_catalog(0, 1)
    games_count = int(json_from_catalog['total'])
    return int(games_count/20) + 1


def parsing():
    max_page = get_max_page()
    page = 1
    offset = 0
    while page != max_page:
        json_from_catalog = get_json_from_catalog(offset, page)
        page_html = json_from_catalog['html']
        soup = BeautifulSoup(page_html, 'lxml')
        product_list = soup.select_one('.product-list')
        for product in product_list.select('div.product-item'):
            goods_title = product.select_one('a.product-item__title-link').text
            release_date = ''

        break
        page += 1
        offset += 20


if __name__ == '__main__':
    # json_from_catalog = get_json_from_catalog(0, 1)
    # save_json(json_from_catalog)
    # response = requests.get(URl_TEST, headers=HEADERS)
    # save_page(response.text, 'page2.html')
    parsing()
