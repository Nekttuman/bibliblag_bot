import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests as req
import datetime

driver = webdriver.Chrome()

class Book():
    def __init__(self, name='', author = '', available = False, where = ''):
        self.name = name
        self.author = author
        self.available = available
        self.where = where

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

def get_books(source):
        """Get page source, take books info and return array of Book objects"""
        books = []

        soup = BeautifulSoup(source, 'html.parser')
                
        return books

def formate_message(books):
        """get array of Books and generate a message for user"""
        message = 'ответ'


        return message
        
def find_books(req_str = ''):
        """get info about book and find it with browser"""
# Открываем окружение, заходим на нужный раздел сайта с помощью webdriver
       
        #http://85.88.171.2:8080/cgi-bin/irbis64r_plus/cgiirbis_64_ft.exe?C21COM=F&I21DBN=KRAJ_FULLTEXT&P21DBN=KRAJ&Z21ID=&S21CNR=5
        driver.get("http://192.168.10.169:8080/cgi-bin/irbis64r_plus/cgiirbis_64_ft.exe?C21COM=F&I21DBN=IBIS_FULLTEXT&P21DBN=IBIS&Z21ID=&S21CNR=5")
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
        driver.quit()

        books = get_books(source)
        return formate_message(books)

def get_events(src = 'https://biblioblag.ru/mibs/plan-meropriyatij'):
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
                n+=1

        events = sorted(events, key= lambda e: e.date)
        
        return events

