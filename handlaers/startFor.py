from aiogram import types
from aiogram.types import CallbackQuery, InlineKeyboardButton

from config import sql, dp
from databasa.functions import Auth_Function
from function.functions import functions


@dp.message_handler(commands='start')
async def welcome(message: types.Message):
    user_id = message.chat.id

    await Auth_Function(message)

    sql.execute("SELECT id FROM channels")
    rows = sql.fetchall()
    join_inline = types.InlineKeyboardMarkup(row_width=1)
    title = 1
    for row in rows:
        all_details = await dp.bot.get_chat(chat_id=row[0])
        url = all_details['invite_link']
        join_inline.insert(InlineKeyboardButton(f"{title} - kanal", url=url))
        title += 1
    join_inline.add(InlineKeyboardButton("✅Obuna bo'ldim", callback_data="check"))
    if await functions.check_on_start(message.from_user.id):
        await message.answer(f"""Assalomu alaykum! """)
    else:
        await message.answer("Botimizdan foydalanish uchun kanalimizga azo bo'ling",
                             reply_markup=join_inline)


@dp.callback_query_handler(text="check")
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    if await functions.check_on_start(user_id):
        await call.answer()
        await call.message.delete()
        await call.message.answer("Xush keldiz")
    else:
        await call.answer(show_alert=True, text="Botimizdan foydalanish uchun kanalimizga azo bo'ling")
