from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
# for i in range(1, pages + 1):
#     browser = webdriver.Firefox(options=options)
#     browser.get("https://steambuy.com/catalog/?page=%i" % i)
#     # Получение HTML-содержимого
#     requiredHtml = browser.page_source
#     soup = BeautifulSoup(requiredHtml, 'html.parser')
#     product_list = soup.select('.product-item')
#     for product in product_list:
#         title = product.select('.product-item__title > a')
#         cost = product.select('.product-item__cost')
#         games.append({'title': title[0].text, 'cost': cost[0].text})
#         print(games[-1])
#     browser.quit()


url = 'https://steambuy.com/catalog/' # ссылка на каталог
options = Options()
options.headless = True


def count_pages():
    browser = webdriver.Firefox(options=options)
    browser.get(url)
    # Получение HTML-содержимого
    requiredHtml = browser.page_source
    soup = BeautifulSoup(requiredHtml, 'html.parser')
    pagination = soup.select('.pagination')
    pages = pagination[0].select('.pagination__btn')
    pages_list = []
    for page in pages:
        pages_list.append(page.text)
    return pages_list[-1]


def main():
    print(count_pages())


if __name__ == "__main__":
    main()
