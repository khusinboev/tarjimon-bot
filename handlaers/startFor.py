from aiogram import types
from aiogram.types import CallbackQuery

from buttons.mButtons import JoinBtn
from config import sql, dp
from databasa.functions import Auth_Function
from function.functions import functions


@dp.message_handler(commands='start')
async def welcome(message: types.Message):
    user_id = message.chat.id
    sql.execute(f"""SELECT user_id FROM public.accounts WHERE user_id = {user_id}""")
    await Auth_Function(message)

    if await functions.check_on_start(message.from_user.id):
        await message.answer(f"""Assalomu alaykum! """)
    else:
        await message.answer("Botimizdan foydalanish uchun kanalimizga azo bo'ling",
                             reply_markup=await JoinBtn(user_id))


@dp.callback_query_handler(text="check")
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    if await functions.check_on_start(user_id):
        await call.answer()
        await call.message.delete()
        await call.message.answer("Xush keldiz")
    else:
        await call.answer(show_alert=True, text="Botimizdan foydalanish uchun kanalimizga azo bo'ling")
