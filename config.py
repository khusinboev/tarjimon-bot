import psycopg2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(find_dotenv())

TOKEN = os.environ['BOT_TOKEN']
adminStart = os.environ['ADMINSTART']
adminPanel = [int(os.environ['ADMINSTART']), int(os.environ['ADMINPANEL'])]

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']

BASE_DIR = str(Path(__file__).resolve().parent.parent)

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

db = psycopg2.connect(
    database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
db.autocommit = True
sql = db.cursor()  # Connection database of Postgres


# apt-get update
# apt-get install tesseract-ocr
#
# # Kerakli tillar uchun til paketlarini o'rnatish
# apt-get install tesseract-ocr-uzb # O'zbekcha (lotin va kiril)
# apt-get install tesseract-ocr-tur # Turkcha
# apt-get install tesseract-ocr-tgk # Tojikcha
# apt-get install tesseract-ocr-eng # Inglizcha
# apt-get install tesseract-ocr-jpn # Yaponiya
# apt-get install tesseract-ocr-ita # Italiya
# apt-get install tesseract-ocr-rus # Ruscha
# apt-get install tesseract-ocr-kor # Koreyscha
# apt-get install tesseract-ocr-ara # Arabcha
# apt-get install tesseract-ocr-chi-sim # Xitoycha (oddiy)
# apt-get install tesseract-ocr-fra # Fransuzcha
# apt-get install tesseract-ocr-deu # Nemischa
# apt-get install tesseract-ocr-hin # Hindcha
# apt-get install tesseract-ocr-aze # Ozarbayjoncha
# apt-get install tesseract-ocr-dar # Afgoncha (Dari)
# apt-get install tesseract-ocr-kaz # Qozog'istoncha
# apt-get install tesseract-ocr-tkm # Turkmancha
# apt-get install tesseract-ocr-kir # Qirg'izcha
# apt-get install tesseract-ocr-amh # Amharic (Efiopiya)
# apt-get install tesseract-ocr-ind # Indoneziya
