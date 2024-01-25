import psycopg2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os


TOKEN = os.environ['BOT_TOKEN']
adminStart = os.environ['ADMINSTART']
adminPanel = [os.environ['ADMINSTART'], os.environ['ADMINPANEL']]

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

db = psycopg2.connect(
    database="users", user='postgres', password='paro!123', host='127.0.0.1', port='5432')
db.autocommit = True
sql = db.cursor()  # Connection database of Postgres
