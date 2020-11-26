import time
import datetime
import config
from scrapper import Scrapper
import scrapper

##################################################################
# тесты времени получения книг с первой страницы
#
#
# str_ex = ['колобок','пушкин онегин','блок','набоков лолита','бред','вдамвамлоиф','вампиры','дней до моего самоубийства',
#             'платонов чевенгур','жизнь волка','ведьмак меч предназначения']

# times = []

# for s in str_ex:
#     t = time.time()
#     scr = Scrapper(config.BookFindServiceUrl)
#     scr.find_books(s)
#     del scr
#     times.append(time.time()-t)

# print("min: ", min(times))
# print("max: ", max(times))
# print("mean: ", sum(times)/len(times), "\n")

# for i in range(len(times)):
#     print(str_ex[i], times[i], sep='  .....  ')
#
####################################################################
