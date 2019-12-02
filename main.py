from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
games = []
pages = 220
for i in range(1, pages+1):
    browser = webdriver.Firefox(options=options)
    browser.get("https://steambuy.com/catalog/?page=%i" % i)
    # Получение HTML-содержимого
    requiredHtml = browser.page_source
    soup = BeautifulSoup(requiredHtml, 'html.parser')
    product_list = soup.select('.product-item')
    for product in product_list:
        title = product.select('.product-item__title > a')
        cost = product.select('.product-item__cost')
        games.append({'title': title[0].text, 'cost': cost[0].text})
        print(games[-1])
    browser.quit()