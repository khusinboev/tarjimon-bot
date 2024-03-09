from aiogram import types
from aiogram.types import CallbackQuery, ChatActions

from buttons.mButtons import JoinBtn, LangsInline
from config import sql, dp, bot, adminStart
from databasa.functions import Auth_Function
from function.functions import functions


@dp.message_handler(commands='start', chat_type=types.ChatType.PRIVATE)
async def welcome(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
    user_id = message.chat.id
    sql.execute(f"""SELECT user_id FROM public.accounts WHERE user_id = {user_id}""")
    await Auth_Function(message)
    try:
        if await functions.check_on_start(message.from_user.id):
            await message.answer(
                text=f"""Assalomu alaykum! Bot 16 ta tilda so'zlar va matnlarni tarjima qiladi. Ikkita ustundan ham tilni 
                tanlash shart\n\nGreetings! The bot translates words and texts in 16 languages. You must select a language 
                from both columns \n\n/lang /lang /lang\n/lang /lang /lang""",
                reply_markup=await LangsInline(message.from_user.id))
        else:
            await message.answer(text="Botimizdan foydalanish uchun kanalimizga azo bo'ling"
                                      "\nSubscribe to our channel to use our bot",
                                 reply_markup=await JoinBtn(user_id))
    except Exception as ex:
        await dp.bot.send_message(chat_id=adminStart, text=f"Error in start: \n\n{ex}")
        pass


@dp.callback_query_handler(text="check", chat_type=types.ChatType.PRIVATE)
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    try:
        if await functions.check_on_start(user_id):
            await call.answer()
            await call.message.delete()
            await call.message.answer(text="Choose languages", reply_markup=await LangsInline(user_id))
        else:
            await call.answer(show_alert=True,
                              text="Botimizdan foydalanish uchun kanalimizga azo bo'ling"
                                   "\nSubscribe to our channel to use our bot")
    except Exception as ex:
        await dp.bot.send_message(chat_id=adminStart, text=f"Error in check: \n\n{ex}")
        pass
