import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests as req
import datetime


class Book:
    def __init__(self, describtion, where_available=''):
        assert isinstance(describtion, str)
        assert isinstance(where_available, str)

        self.describtion = self.prepare(describtion)
        self.where_available = self.prepare(where_available)

    def prepare(self, st):
        while '  ' in st:
            st = st.replace('  ', '')
        if '(1)' in st:
            st = st.replace('(1)', '')
        return st

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
        '''return bool value find/not find, init self.source with first page source'''
        driver = self.driver
        search = driver.find_element_by_css_selector("#SEARCH_STRING")
        driver.find_element_by_css_selector(
            "#ctrl_toggleExtendedSearchFields_text").click()
        select = Select(driver.find_element_by_name('A34_main'))
        select.select_by_visible_text('Книги в целом')
        search.send_keys(req_str)
        driver.find_element_by_name("C21COM1").click()
        # проверка наличия книги
        try:
            notFound = driver.find_element_by_css_selector('td[colspan="4"]')
        except ValueError:
            pass  
        if notFound.text[:48] == 'Нет результатов для данного запроса. Попробуйте:':
            return 0
        else:
            self.source = driver.page_source
            return 1

    def get_all_books(self):
        def get_books_desc_from_page(source):
            soup = BeautifulSoup(source, 'html.parser')
            tables = soup.find_all('table', attrs={'style': 'width:100%;border:1px;font-size:11px;'})
            for note in tables:
                note = note.text
                places = ''
                if 'Свободны' in note:
                    places = note[note.index('Свободны')+10:].split(', ')
                
                if 'ISBN' in note:
                    note = note[note.index('.') + 1:note.index('ISBN')+22]
                elif 'экз.' in note:
                    note = note[note.index('.') + 1:note.index('экз.')+4]
                    
                note = note[note.index('.') + 7:]
                for pls in places:
                    self.books.append(Book(note, pls))

        driver = self.driver
        curr_source = self.source
        END = False
        get_books_desc_from_page(curr_source)  # берем инфу с первой страницы
        while not END:                         # здесь со всех последующих
            # поиск кнопки для перехода на следующую страницу
            portions = driver.find_elements_by_class_name('portion')
            if len(portions) != 0:
                for navElem in portions:
                    if navElem.text == 'Следующая':
                        END = False
                        navElem.click()
                        curr_source = driver.page_source
                        break
                    else:
                        END = True
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
