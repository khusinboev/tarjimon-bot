from aiogram import types
from aiogram.types import CallbackQuery
from deep_translator import GoogleTranslator

from buttons.mButtons import Group_Lang_Inline
from config import dp, sql, bot
from databasa.functions import Auth_Group_Function
from function.functions import GroupCheckLang
from handlaers.user_translator import CallFilter


@dp.message_handler(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], commands=['start', 'lang', 'help'])
async def group_handle(message: types.Message):
    await Auth_Group_Function(message.chat.id, message.chat.type)
    if 'help' in message.text:
        await message.answer("Murojaat uchun/For reference admin: @coder_admin_py")
    if 'start' in message.text:
        await message.answer("Bot started. /lang")
    else:
        await message.answer("Kerakli tilni tanlang/Choose your language", reply_markup=await Group_Lang_Inline(message.chat.id))


@dp.callback_query_handler(text=CallFilter(), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def check(call: CallbackQuery):
    await Auth_Group_Function(call.message.chat.id, call.message.chat.type)
    await GroupCheckLang(call)
    await call.answer()
    try:
        await call.message.edit_reply_markup(await Group_Lang_Inline(call.message.chat.id))
    except:
        pass


@dp.message_handler(lambda message: message.reply_to_message['from']['username'] == bot.get_me().username, content_types=types.ContentTypes.TEXT,
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def group_handle(message: types.Message):
    await Auth_Group_Function(message.chat.id, message.chat.type)
    chat_id = message.chat.id
    sql.execute(f"""select in_lang from public.group_langs where chat_id={chat_id}""")
    lang_in = sql.fetchone()[0]

    sql.execute(f"""select out_lang from public.group_langs where chat_id={chat_id}""")
    lang_out = sql.fetchone()[0]

    translator = GoogleTranslator(source=lang_in, target=lang_out)
    text = translator.translate(message.text)
    try:
        await message.reply(text=f"<code>{text}</code>", parse_mode="html")
    except:
        await message.answer(text=f"<code>{text}</code>", parse_mode="html")
