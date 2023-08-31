import psycopg2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = "5597490636:AAHpFyraZFQOCfP5zCLocResahxlwDe0ygI"  # The bot token you want to run
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

db = psycopg2.connect(
    database="users", user='postgres', password='paro!123', host='127.0.0.1', port='5432')
db.autocommit = True
sql = db.cursor()  # Connection database of Postgres

# Admins' ids
adminStart = 1918760732  # Firstly started send to message admin
adminPanel = [1918760732, 5246872049]  # Admins id for admin panel
