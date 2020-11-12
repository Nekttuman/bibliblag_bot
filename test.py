from bs4 import BeautifulSoup
import requests as req
import datetime
import config
from scrapper import Scrapper
import scrapper




s = 'ведьмак меч предназначения'#input()
scr = Scrapper(config.BookFindServiceUrl_alt)
scr.find(s)
scr.show_books()

scr.close()


# class Event:
#     def __init__(self, date, name, place, describtion, category):
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

#     def show(self):
#         print(self.make_message_str())



# resp = req.get("https://biblioblag.ru/mibs/plan-meropriyatij")
# soup = BeautifulSoup(resp.text, 'html.parser')

# records = soup.find_all('body')

# print(records)

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



