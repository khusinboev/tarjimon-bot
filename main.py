from aiogram.utils import executor
from aiogram import types

from databasa.functions import CreateBasa
from handlaers.startFor import *
from handlaers.admin_panel import *
from handlaers.user_translator import *
from handlaers.group_translator import *

from config import dp, adminStart, BASE_DIR
import os


async def on_startup(dp):
    await dp.bot.send_message(chat_id=adminStart, text="Successful. Bot started!")
    if not os.path.exists(BASE_DIR + "Audios"):
        os.makedirs(BASE_DIR + "Audios")
    if not os.path.exists(BASE_DIR + "photos"):
        os.makedirs(BASE_DIR + "photos")
    if not os.path.exists(BASE_DIR + "audio_tr"):
        os.makedirs(BASE_DIR + "audio_tr")
    print(await bot.get_me())
    await CreateBasa()


@dp.message_handler(content_types="any", chat_type=types.ChatType.PRIVATE)
async def helper(message: types.Message):
    message_id = message.message_id
    await dp.bot.copy_message(chat_id=message.from_user.id, from_chat_id=message.from_user.id, message_id=message_id)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
