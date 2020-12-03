import requests
import random
from bs4 import BeautifulSoup
import os
import time
import json
import re
import db
import httplib2
from pymysql.err import OperationalError

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

GENRES = {'Аркады': 1, 'Экшен': 2, 'Ролевые': 3, 'Симуляторы': 4, 'Логические': 5, 'Файтинг': 6,
          'MMO': 7, 'Приключение': 8, 'Гонки': 9, 'Спорт': 10, 'Стратегии': 11, 'Прочее': 12}


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


def save_image(url, image_name):
    h = httplib2.Http('.cache')
    response, content = h.request(url)
    with open("{}".format(image_name), 'wb') as out:
        out.write(content)


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


def parse_genre(data: dict):
    genre = str(GENRES['Прочее'])
    genres_from_data = data['response']['data']['goods'][0]['genre'].split(', ')
    for parsed_genre in genres_from_data:
        if parsed_genre in GENRES:
            genre = str(GENRES[parsed_genre])
            break
    return genre


def parse_description(soup):
    description = ''
    if soup.select_one('div.product-desc__article'):
        description = str(soup.select_one('div.product-desc__article'))
    return description


def parse_systemreq(soup):
    systemreq = ''
    if soup.select_one('#system'):
        systemreq = str(soup.select_one('#system'))
    return systemreq


def parse_platform(soup):
    platform = ''
    units = soup.select('.product-detail__unit')
    for unit in units:
        if 'Работает на:' in unit.text:
            platform = ', '.join([el.text for el in unit.select('.product-detail__value-link')])
            break
    return platform


def parse_lang(soup):
    lang = ''
    units = soup.select('div.product-about__option-unit')
    for unit in units:
        if 'Язык:' in unit.text:
            lang = unit.select_one('div.product-about__option-value').text
            break
    return lang


def parse_activation(data: dict):
    return data['response']['data']['goods'][0]['activation']


def parse_price(soup):
    price_text = soup.select_one('.product-price__cost').text
    if price_text == "Скоро":
        price = 1999
    else:
        price = int(price_text.replace(' р', ''))
    return price


def parse_real_price(soup):
    real_price_block = soup.select_one('.product-price__discount-cost')
    real_price = None
    if real_price_block:
        real_price = soup.select_one('.product-price__discount-cost').text.replace(' р', '')
    return real_price


def parse_publisher(soup):
    publisher = ''
    units = soup.select('.product-detail__unit')
    for unit in units:
        if 'Издатель:' in unit.text:
            publisher = ', '.join([el.text for el in unit.select('.product-detail__value-link')])
            break
    return publisher


def parse_in_stock(data: dict):
    if data['response']['data']['goods'][0]['available']:
        return 'y'
    else:
        return 'n'


def parse_video(soup):
    video = ''
    video_link_block = soup.select_one('.product-media__link.product-media__link_video')
    if video_link_block:
        re_search = re.search('https://www.youtube.com/embed/(.+)\?', video_link_block['href'])
        if re_search:
            video = re_search.group(1)
    return video


def parse_data(product_soup, game_soup, game_json, id):
    good_title = product_soup.select_one('a.product-item__title-link').text
    new_tab, leader_tab, preorder_tab, offer_day = parse_tabs(product_soup)
    release_date = parse_realese_date(product_soup)
    genre = parse_genre(game_json)
    description = parse_description(game_soup)
    systemreq = parse_systemreq(game_soup)
    thumbnail = '{}.png'.format(id)
    platform = parse_platform(game_soup)
    lang = parse_lang(game_soup)
    if len(lang) > 25:
        lang = lang.split(' ')[0]
    activation = parse_activation(game_json)
    price = parse_price(game_soup)
    real_price = parse_real_price(game_soup)
    if real_price is None:
        real_price = str(price)
    publisher = parse_publisher(game_soup)
    good_type = 'item'
    if preorder_tab:
        good_type = 'comming'
    in_stock = parse_in_stock(game_json)
    digiseller_id = id
    video = parse_video(game_soup)
    views = 0
    return good_title, release_date, genre, description, systemreq, thumbnail, platform, lang, activation, real_price, \
           publisher, good_type, price, new_tab, leader_tab, preorder_tab, offer_day, in_stock, digiseller_id, video, \
           views


def parsing_games(load_local_catalog_html=True,
                  load_local_game_html=True,
                  load_local_json=True,
                  download_image=True,
                  save_data_in_db=True,
                  html_save=True,
                  is_continue=False):
    if load_local_catalog_html:
        catalog = parsing_catalog(load_local_html=True)
    else:
        catalog = parsing_catalog(load_local_html=False, html_save=html_save)
    for page_html in catalog:
        page_soup = BeautifulSoup(page_html, 'lxml')
        for product_soup in page_soup.select('div.product-item'):
            id = int(product_soup.select_one('.product-item__btn')['data-id'])
            print(id)
            game_html_path = '{}/{}.html'.format(GAME_HTML_PATH, id)
            game_json_path = '{}/{}.json'.format(GAME_JSON_PATH, id)
            if is_continue:
                if os.path.isfile(game_html_path) and os.path.isfile(game_json_path):
                    continue
            url_html = HOST + product_soup.select_one('a.product-item__title-link')['href']
            url_api = URl_API.format(id)
            game_html = get_game_html(game_html_path, url_html, load_local_game_html)
            game_json = get_game_json(game_json_path, url_api, load_local_json)
            if not game_html or not game_json:
                continue
            if save_data_in_db:
                game_soup = BeautifulSoup(game_html, 'lxml')
                data = parse_data(product_soup, game_soup, game_json, id)
                print(data)
                if 'Тестовая покупка' in data[0]:
                    continue
                db.add_game_in_db(data)
            if download_image:
                img_url = product_soup.select_one('.product-item__img').select_one('img')['src']
                save_image(img_url, '{}/{}.png'.format(IMAGES_PATH, id))
            if html_save:
                save_page(game_html, game_html_path)
                save_json(game_json, game_json_path)


if __name__ == '__main__':
    while True:
        try:
            parsing_games(load_local_catalog_html=True,
                          load_local_game_html=True,
                          load_local_json=True,
                          download_image=False,
                          save_data_in_db=True,
                          html_save=False,
                          is_continue=False)
            break
        except ConnectionError:
            pass
