from aiogram.utils import executor

from databasa.functions import CreateBasa
from handlaers.startFor import *
from handlaers.admin_panel import *
from config import dp

async def on_startup(dp):
    await dp.bot.send_message(chat_id=1918760732, text="Successful. Bot started!")
    await CreateBasa()

@dp.message_handler(content_types="any")
async def helper(message: types.Message):
    id = message.message_id
    await dp.bot.copy_message(chat_id=message.from_user.id, from_chat_id=message.from_user.id, message_id=id)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
