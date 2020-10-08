import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


class Book():
    def __init__(self, name='', author = '', available = False, where = ''):
        self.name = name
        self.author = author
        self.available = available
        self.where = where


def extract_data(source):
    books = []

    soup = BeautifulSoup(source, 'html.parser')

    return books

def find_books_in_browser(req_str = ''):
# Открываем окружение, находим все нужные элементы с помощью webdriver
        driver = webdriver.Chrome()
        driver.get("http://85.88.171.2:8080/cgi-bin/irbis64r_plus/cgiirbis_64_ft.exe?C21COM=F&I21DBN=KRAJ_FULLTEXT&P21DBN=KRAJ&Z21ID=&S21CNR=5")
        submit_button = driver.find_element_by_css_selector('[value="Войти как Гость"]')
        submit_button.click()
        print(submit_button)
        select = Select(driver.find_element_by_css_selector("[name='I21DBN']"))
        select.select_by_visible_text('Основной электронный каталог')
        search = driver.find_element_by_css_selector("#SEARCH_STRING")
        driver.find_element_by_css_selector("#ctrl_toggleExtendedSearchFields_text").click()

        select = Select(driver.find_element_by_name('A34_main'))
        select.select_by_visible_text('Книги в целом')
# Отправляем запрос
        search.send_keys(req_str)
        driver.find_element_by_name("C21COM1").click()

        source = driver.page_source

# close
        time.sleep(10)
        driver.quit()
        books = extract_data(source)
        return books


# if __name__ == "__main__":
