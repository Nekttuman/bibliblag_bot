from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests as req


class Book:
    def __init__(self, describtion, libraries=[]):
        assert isinstance(describtion, str)

        self.describtion = self.__prepare(describtion)
        self.libraries = list(map(self.__prepare, libraries))

    def __prepare(self, st):
        while '  ' in st:
            st = st.replace('  ', ' ')
        if '(1)' in st:
            st = st.replace('(1)', '')
        while '..' in st:
            st = st.replace('..', '.')
        if 'Держ' in st:
            st = st[: st.find('Держ')]
        if 'Содерж' in st:
            st = st[:st.find('Содерж')]
        if 'Рубрик' in st:
            st = st[:st.find('Рубрик')]
        if 'Кл.слова' in st:
            st = st[:st.find('Кл.слова')]
        return st

    def show(self):
        print(self.describtion, *self.libraries, sep='\n', end='\n\n')
    
    def to_str(self):
        string = self.describtion + '\n' + 'Библиотеки:' + '\n'
        for lib in self.libraries:
            string += '🔸' + lib +'\n'
        return string


class Scrapper:
    events = []
    source = ''
    num_books = 0
    
    def __init__(self, book_url):
        self.driver = webdriver.Chrome()
        self.driver.get(book_url)
        submit_button = self.driver.find_element_by_css_selector(
            '[value="Войти как Гость"]')
        submit_button.click()
        select = Select(
            self.driver.find_element_by_css_selector("[name='I21DBN']"))
        select.select_by_visible_text('Основной электронный каталог')
        self.driver.find_element_by_css_selector(
            "#ctrl_toggleExtendedSearchFields_text").click()
        select = Select(self.driver.find_element_by_name('A34_main'))
        select.select_by_visible_text('Книги в целом')

    def find_books(self, req_str):
        '''return Book[], init self.source with first page source'''
        search = self.driver.find_element_by_css_selector("#SEARCH_STRING")
        search.send_keys(req_str)
        self.driver.find_element_by_name("C21COM1").click()
        # проверка наличия книги
        try:
            notFound = self.driver.find_element_by_css_selector(
                'td[colspan="4"]')
        except ValueError:
            pass
        if notFound.text[:48] == 'Нет результатов для данного запроса. Попробуйте:':
            return None
        else:
            self.source = self.driver.page_source
            books = self.__get_books_from_page()

            return books

    def find_next(self):
        if self.__go_next_page():
            books = self.__get_books_from_page()
            return books
        else:
            return []

    def __get_books_from_page(self):
        soup = BeautifulSoup(self.source, 'html.parser')
        books = []
        tables = soup.find_all(
            'table', attrs={'style': 'width:100%;border:1px;font-size:11px;'})
        for note in tables:
            note = note.text
            places = []
            if 'Всего:' in note:
                places = note[note.index('Всего:')+10:note.index('Свободны')].split(', ')

            if 'ISBN' in note:
                note = note[note.index('.') + 1:note.index('ISBN')+22]
            elif 'экз.' in note:
                note = note[note.index('.') + 1:note.index('экз.')+4]

            note = note[note.index('.') + 7:]
            books.append(Book(note, places))
        return books

    def __go_next_page(self):                         # здесь со всех последующих
        navbar = self.driver.find_elements_by_class_name('portion')
        if len(navbar) == 0:                # если навбара нет, то это единственная страница
            return False
        for navElem in navbar:
            if navElem.text == 'Следующая':
                navElem.click()
                self.source = self.driver.page_source
                return True
        return False

    def close_browser(self):
        self.driver.close()

    def __del__(self):
        self.driver.quit()
