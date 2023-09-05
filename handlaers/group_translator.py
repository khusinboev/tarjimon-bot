from aiogram import types

from config import dp


@dp.message_handler(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def group_handle(message: types.Message):
    await message.answer(message.as_json())
