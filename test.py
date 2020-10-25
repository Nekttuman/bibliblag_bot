from bs4 import BeautifulSoup
import requests as req
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datetime

req_str = 'сапковский ведьмак'
driver = webdriver.Chrome()


driver.get("http://85.88.171.2:8080/cgi-bin/irbis64r_plus/cgiirbis_64_ft.exe?C21COM=F&I21DBN=KRAJ_FULLTEXT&P21DBN=KRAJ&Z21ID=&S21CNR=5")
submit_button = driver.find_element_by_css_selector('[value="Войти как Гость"]')
submit_button.click()
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
#driver.quit()

soup = BeautifulSoup(source, 'html.parser')
tables = soup.find_all('table', attrs = {'style':'width:100%;border:1px;font-size:11px;'})
for book in tables:
    help(book)
    book = book.text
    book = book[book.index('.') + 1:book.index('(в пер.)')]
    book = book[book.index('.') + 7:]
    print(book)

# поиск кнопки для перехода на следующую страницу
portions = driver.find_elements_by_class_name('portion')
END = False
next = None
for page in portions:
    if page.text == 'Следующая':
        END = False
        next = page
        break
    else:
        END = True


#     def __init__(self, date, name, place, describtion, category = ''):
#         self.date = date
#         self.name = name
#         self.place = place
#         self.describtion = describtion
#         self.category = category

#     def make_message_str(self):
#         s = '''{1}  {0}
# {4}

# {2}

# Подробнее: {3}'''.format(self.name, self.date, self.place, self.describtion, self.category)
#         return s


# resp = req.get("https://biblioblag.ru/mibs/plan-meropriyatij")
 
# soup = BeautifulSoup(resp.text, 'html.parser')
# table = soup.tbody

# records = soup.find_all('tr')
# events = []
# for rec in records[1:]:
#     cel = rec.find_all('td')
#     name = cel[1].text[1:-1]
#     date = cel[0].text
    
    
#     date = date.replace("\n", "")
#     date = date.replace(" ", "")
#     try:
#         date = datetime.date(2020, int(date[3:5]), int(date[:2]))
#     except ValueError:
#         date = date[1:]
#         date = datetime.date(2020, int(date[3:5]), int(date[:2]))
            
#     place = cel[2].text[1:-1]
#     desc = cel[3].text[1:-1]
#     category = cel[3].find('strong').text
#     event = Event(date, name, place, desc, category)
#     events.append(event)

# events = sorted(events, key= lambda e: e.date)
# for i in events:
#     print(i.make_message_str())



