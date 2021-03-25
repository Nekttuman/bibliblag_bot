import time
import datetime
import config
from scrapper import Scrapper
import scrapper
from loguru import logger 

logger.add("logs/debug.log", format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message}", level="DEBUG", rotation="100 MB", compression="zip", backtrace=True, diagnose=True)

logger.debug("hello, {user}!", user = 'hell')

def f(a):
    return 1/a

f(0)