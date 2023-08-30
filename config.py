import psycopg2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = "5597490636:AAHpFyraZFQOCfP5zCLocResahxlwDe0ygI"
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

db = psycopg2.connect(
    database="users", user='postgres', password='paro!123', host='127.0.0.1', port='5432')
db.autocommit = True
sql = db.cursor()
