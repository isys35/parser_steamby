import requests
import random
from bs4 import BeautifulSoup
import os
import time
import json

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

HOST = 'https://steambuy.com'

CATALOG_HTML_PATH = 'catalog_html'
GAME_HTML_PATH = 'game_html'
GAME_JSON_PATH = 'game_json'
IMAGES_PATH = 'images'


# GENRES = db.get_genres()


def make_dirs():
    os.mkdir(CATALOG_HTML_PATH)
    os.mkdir(GAME_HTML_PATH)
    os.mkdir(GAME_JSON_PATH)
    os.mkdir(IMAGES_PATH)


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
    return int(games_count / 20) + 1


def parsing_catalog(html_save=True, load_local_html=False):
    if load_local_html:
        for page_html in os.listdir(CATALOG_HTML_PATH):
            print(page_html)
            with open('{}//{}'.format(CATALOG_HTML_PATH, page_html), 'r', encoding='utf8') as page_html_file:
                page_html = page_html_file.read()
            yield page_html
    else:
        max_page = get_max_page()
        page = 1
        offset = 0
        while page != max_page + 1:
            print(page)
            json_from_catalog = get_json_from_catalog(offset, page)
            page_html = json_from_catalog['html']
            if html_save:
                save_page(page_html, 'catalog_html/{}.html'.format(page))
            page += 1
            offset += 20
            yield page_html


def get_game_html(game_html_path, url_html, load_local_game_html=False):
    if load_local_game_html:
        if os.path.isfile(game_html_path):
            with open(game_html_path, 'r', encoding='utf-8') as game_file:
                game_html = game_file.read()
        else:
            return
    else:
        response = requests.get(url_html, headers=HEADERS)
        game_html = response.text
        time.sleep(1)
    return game_html


def get_game_json(game_json_path, url_api, load_local_json=False):
    if load_local_json:
        if os.path.isfile(game_json_path):
            with open(game_json_path, 'r', encoding='utf-8') as game_file_json:
                game_json = json.load(game_file_json)
        else:
            return
    else:
        response = requests.get(url_api)
        game_json = response.json()
        time.sleep(1)
    return game_json


def parse_tabs(soup):
    label = soup.select_one('span.game-item__label')
    new_tab = '0'
    leader_tab = 0
    preorder_tab = 0
    offer_day = 'n'
    if label:
        if 'РЕЛИЗ' in label.text:
            preorder_tab = 1
        if 'НОВИНКА' in label.text:
            new_tab = '1'
        if 'Предзаказ' in label.text:
            preorder_tab = 1
    return new_tab, leader_tab, preorder_tab, offer_day


def parse_realese_date(soup):
    realese_date = ''
    units = soup.select('.product-item__unit')
    for unit in units:
        if 'ДАТА ВЫХОДА:' in unit.text:
            realese_date = unit.select_one('.product-item__unit-value').text
            break
    return realese_date


def parsing_games(load_local_catalog_html=True,
                  load_local_game_html=True,
                  load_local_json=True,
                  html_save=True):
    if load_local_catalog_html:
        catalog = parsing_catalog(load_local_html=True)
    else:
        catalog = parsing_catalog(load_local_html=False, html_save=html_save)
    for page_html in catalog:
        page_soup = BeautifulSoup(page_html, 'lxml')
        for product in page_soup.select('div.product-item'):
            id = product.select_one('.product-item__btn')['data-id']
            print(id)
            game_html_path = '{}/{}.html'.format(GAME_HTML_PATH, id)
            game_json_path = '{}/{}.json'.format(GAME_JSON_PATH, id)
            url_html = HOST + product.select_one('a.product-item__title-link')['href']
            url_api = URl_API.format(id)
            game_html = get_game_html(game_html_path, url_html, load_local_game_html)
            game_json = get_game_json(game_json_path, url_api, load_local_json)
            if not game_html or not game_json:
                continue
            game_soup = BeautifulSoup(game_html, 'lxml')
            good_title = product.select_one('a.product-item__title-link').text
            new_tab, leader_tab, preorder_tab, offer_day = parse_tabs(product)
            release_date = parse_realese_date(product)
            print(good_title, release_date, new_tab, leader_tab, preorder_tab, offer_day)
            if html_save:
                save_page(game_html, game_html_path)
                save_json(game_json, game_json_path)


# soup = BeautifulSoup(page_html, 'lxml')
# product_list = soup.select_one('.product-list')
# for product in product_list.select('div.product-item'):
#     goods_title = product.select_one('a.product-item__title-link').text
#     release_date = ''


if __name__ == '__main__':
    # json_from_catalog = get_json_from_catalog(0, 1)
    # save_json(json_from_catalog)
    # response = requests.get(URl_TEST, headers=HEADERS)
    # save_page(response.text, 'page2.html')
    parsing_games(load_local_catalog_html=False,
                  load_local_game_html=False,
                  load_local_json=False,
                  html_save=True)
