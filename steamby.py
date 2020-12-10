import random
import requests
from bs4 import BeautifulSoup
import csv

# Заголовок запроса
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

# Ссылка для получения данных с сайта
URL = 'https://steambuy.com/ajax/_get.php?rnd={}&offset={}&region_free=0&sort=cnt_sell' \
      '&sortMode=descendant&view=extended&a=getcat&q=&series=&izdatel=&currency=wmr&curr=&currMaxSumm[wmr]=3000' \
      '&currMaxSumm[wmz]=100&currMaxSumm[wme]=70&currMaxSumm[wmu]=1000&letter=&limit=0&page={}&minPrice=0' \
      '&maxPrice=9999&minDate=0&maxDate=0&deleted=0&no_price_range=0&records=20'

# Путь к файлу хранения данных
DATA_FILE_CSV = 'data.csv'


def get_json_from_catalog(offset, page):
    """
    Получение данных в формате JSON
    """
    url = URL.format(random.random(), offset, page)  # Подставляем нужные значения в ссылку
    response = requests.get(url, headers=HEADERS)  # Получение ответа
    return response.json()


def get_max_page():
    """
    Получение максимальной страницы из каталога
    """
    json_from_catalog = get_json_from_catalog(0, 1)
    games_count = int(json_from_catalog['total'])
    return int(games_count / 20) + 1


def write_scv_headers(file_name=DATA_FILE_CSV):
    """
    Создание шапки в .csv файле
    """
    with open(file_name, 'w', encoding='utf8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['id', 'Название', 'Цена'])


def save_data(data, file_name=DATA_FILE_CSV):
    """
    Сохранение данных
    """
    with open(file_name, 'a', encoding='utf8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerows(data)


def get_data_from_html(html):
    """
    Получение данных из html страницы
    """
    soup = BeautifulSoup(html, 'lxml')
    products_data = []
    for product_soup in soup.select('div.product-item'):
        product_id = int(product_soup.select_one('.product-item__btn')['data-id'])
        product_name = product_soup.select_one('a.product-item__title-link').text
        product_price_soup = product_soup.select_one('.product-item__cost')
        if product_price_soup:
            product_price = product_price_soup.text
        else:
            product_price = None
        product_data = [product_id, product_name, product_price]
        products_data.append(product_data)
    return products_data


def parser():
    """
    ПАРСЕР
    """
    write_scv_headers()
    max_page = get_max_page()
    page = 1
    offset = 0
    while page != max_page + 1:
        print('Страница {}/{}'.format(page, max_page))
        json_from_catalog = get_json_from_catalog(offset, page)
        page_html = json_from_catalog['html']
        data = get_data_from_html(page_html)
        save_data(data)
        page += 1
        offset += 20


if __name__ == '__main__':
    parser()
