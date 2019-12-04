from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import xlwt
url = 'https://steambuy.com/catalog/'  # ссылка на каталог
options = Options()
options.headless = True


def benchmark(func):
    import time

    def wrapper():
        start = time.time()
        return_value = func()
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))
        return return_value
    return wrapper


@benchmark
def count_pages():
    print('Определение кол-ва страниц...')
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
    browser.quit()
    print('Кол-во страниц ' + pages_list[-1])
    return pages_list[-1]


def save_data_txt(data):
    f = open('data.txt', 'w',encoding="utf-8")
    for el in data:
        f.write(el['title'] + ',' + str(el['cost']) + '\n')
    f.close()


def save_data_excel(data):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Data')
    keys = [k for k in data[-1].keys()]
    ws.col(0).width = 15000
    ws.write(0, 0, keys[0])
    ws.write(0, 1, keys[1])
    for id in range(0, len(data)):
        ws.write(id+1, 0, data[id][keys[0]])
        ws.write(id+1, 1, data[id][keys[1]])
    wb.save('data.xls')

# test git

def main():
    pages = int(count_pages())
    games = []
    exceptions_titles = ['SILVER', 'DIAMOND - Игры от 899 рублей', 'GOLD']
    for i in range(1, pages + 1):
        print('страница %i' %i)
        browser = webdriver.Firefox(options=options)
        page_url = '?page=%i' % i
        browser.get(url + page_url)
        requiredHtml = browser.page_source
        soup = BeautifulSoup(requiredHtml, 'html.parser')
        product_list = soup.select('.product-item')
        for product in product_list:
            title = product.select('.product-item__title > a')
            cost = product.select('.product-item__cost')
            if cost[0].text != 'СКОРО' and title[0].text not in exceptions_titles:
                cost = cost[0].text.replace(' р', '')
                games.append({'title': title[0].text, 'cost': float(cost)})
                print(games[-1]['title'])
        browser.quit()
        save_data_txt(games)
        save_data_excel(games)


if __name__ == "__main__":
    main()

