from typing import Dict
import datetime
import random

PORT = 8001
DEFAULT_DATA_SIZE = 1024

NAME = 'NAME'
TIME = 'TIME'
RAND = 'RAND'
QUIT = 'BYE'

def name() -> str:
    return 'Omri\'s commands server'

def time() -> str:
    return datetime.datetime.now().strftime('%H:%M')

def rand() -> str:
    return str(random.randint(1, 10))

def quit() -> str:
    return 'Closing Server and Client'