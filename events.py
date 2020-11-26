import datetime
import requests as req
from bs4 import BeautifulSoup
import config

"""предоставляет список мероприятий events, обновляет его каждый день"""

last_update =  datetime.date(2020, 11, 2)

events = []

class Event:
    def __init__(self, date, name, place, describtion, category):
        self.date = date
        self.name = name
        self.place = place
        self.describtion = describtion
        self.category = category

    def show(self):
        print(self.date, self.name, self.place, self.describtion, self.category)

if last_update < datetime.date.today():
    resp = req.get(config.EventSrc)
    soup = BeautifulSoup(resp.text, 'html.parser')
    records = soup.find_all('tr')


    last_events = events
    events = []


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
        # if date < datetime.date(2020, 10, 11):
        #     continue
        place = cel[2].text[1:-1]
        desc = cel[3].text[1:-1]
        category = cel[1].find('strong').text

        event = Event(date, name, place, desc, category)
        events.append(event)

        event.show()

    # except Exception as error:
    #     events = last_events
    #     f = open('raised_exceptions.log', 'a')
    #     f.write(datetime.date.month + '.' + datetime.date.day + '\n' + error)
    #     f.close()

    events = sorted(events, key=lambda e: e.date)

