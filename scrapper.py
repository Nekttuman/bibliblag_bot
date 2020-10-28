import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests as req
import datetime


class Book:
    def __init__(self, describtion, where_available=''):
        self.describtion = describtion
        self.where_available = where_available

    def show(self):
        print(self.describtion, self.where_available, sep='\n', end='\n\n')


class Scrapper:
    driver = webdriver.Chrome()
    books = []
    source = ''

    def __init__(self, url):
        driver = self.driver
        driver.get(url)
        submit_button = driver.find_element_by_css_selector(
            '[value="Войти как Гость"]')
        submit_button.click()
        select = Select(driver.find_element_by_css_selector("[name='I21DBN']"))
        select.select_by_visible_text('Основной электронный каталог')

    # Отправляем запрос
    def find(self, req_str):
        driver = self.driver
        search = driver.find_element_by_css_selector("#SEARCH_STRING")
        driver.find_element_by_css_selector(
            "#ctrl_toggleExtendedSearchFields_text").click()
        select = Select(driver.find_element_by_name('A34_main'))
        select.select_by_visible_text('Книги в целом')

        search.send_keys(req_str)
        driver.find_element_by_name("C21COM1").click()
        self.source = driver.page_source

    def get_all_books(self):
        def get_books_desc_from_page(source):
            soup = BeautifulSoup(source, 'html.parser')
            tables = soup.find_all(
                'table', attrs={'style': 'width:100%;border:1px;font-size:11px;'})
            for note in tables:
                note = note.text
                note = note[note.index('.') + 1:note.index('ISBN')+22]
                note = note[note.index('.') + 7:]
            # нужен скраппер доступных мест
                self.books.append(Book(note))

        driver = self.driver
        curr_source = self.source
        END = False
        get_books_desc_from_page(curr_source)  # с первой страницы
        while not END:
            # поиск кнопки для перехода на следующую страницу
            portions = driver.find_elements_by_class_name('portion')
            for page in portions:
                if page.text == 'Следующая':
                    END = False
                    page.click()
                    curr_source = driver.page_source
                    break
            else:
                END = True
            get_books_desc_from_page(curr_source)

    def formate_message(self, books):
        """get array of Books and generate a message for user"""
        message = 'ответ'
        return message

    def show_books(self):
        for i in range(len(self.books)):
            print(i)
            self.books[i].show()
            
    def close(self):
        self.driver.quit()


def get_events(src='https://biblioblag.ru/mibs/plan-meropriyatij'):
    resp = req.get(src)
    today = datetime.date(2020, 10, 1)

    soup = BeautifulSoup(resp.text, 'html.parser')

    records = soup.find_all('tr')
    events = []
    n = 1
    for rec in records[1:]:
        cel = rec.find_all('td')
        name = cel[1].text[1:-1]
        date = cel[0].text

        date = date.replace("\n", "")
        date = date.replace(" ", "")
        try:
            date = datetime.date(2020, int(date[3:5]), int(date[:2]))
        except ValueError:
            date = date[1:]
            date = datetime.date(2020, int(date[3:5]), int(date[:2]))
        if date < today:
            continue
        place = cel[2].text[1:-1]
        desc = cel[3].text[1:-1]
        category = cel[1].find('strong').text

        event = Event(date, name, place, desc, category, n)
        events.append(event)
        n += 1

    events = sorted(events, key=lambda e: e.date)
    return events


class Event:
    def __init__(self, date, name, place, describtion, category, num):
        self.date = date
        self.name = name
        self.place = place
        self.describtion = describtion
        self.category = category
        self.num = num

    def make_message_str(self):
        s = '''{1}  {0}
{4}

{2}

Подробнее: {3}'''.format(self.name, self.date, self.place, self.describtion, self.category)
        return s
