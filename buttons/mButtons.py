from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton

from config import sql, dp
from function.functions import LangList, UserLangs

main_btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_btn.add("📊Statistika", "🔧Kanallar", "📤Reklama", "♻️ Tozalash")

channel_btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
channel_btn.add("➕Kanal qo'shish", "❌Kanalni olib tashlash")
channel_btn.add("📋 Kanallar ro'yxati", "🔙Orqaga qaytish")

reklama_btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
reklama_btn.add("📨Forward xabar yuborish", "📬Oddiy xabar yuborish", "🔙Orqaga qaytish")

async def JoinBtn(user_id):
    sql.execute("SELECT chat_id FROM public.mandatorys")
    rows = sql.fetchall()
    join_inline = types.InlineKeyboardMarkup(row_width=1)
    title = 1
    for row in rows:
        all_details = await dp.bot.get_chat(chat_id=row[0])
        url = all_details['invite_link']
        join_inline.insert(InlineKeyboardButton(f"{title} - kanal", url=url))
        title += 1
    join_inline.add(InlineKeyboardButton("✅Obuna bo'ldim", callback_data="check"))

    return join_inline

async def LangsInline(user_id):
    user_in, user_out = await UserLangs(user_id)

    sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
    tts = sql.fetchone()[0]

    lang_ins, lang_outs = await LangList()

    langs_inline = types.InlineKeyboardMarkup(row_width=2)
    for lang_in, lang_out in zip(lang_ins, lang_outs):
        Nin = ""
        Nout = ""
        if user_in == lang_in:
            Nin = "✅"
        if user_out == lang_out:
            Nout = "✅"
        langs_inline.add(InlineKeyboardButton(Nin+lang_in, callback_data=lang_in))
        langs_inline.insert(InlineKeyboardButton(Nout+lang_out, callback_data=lang_out))
    TTS = "☑️"
    if tts:
        TTS = "✅"
    langs_inline.add(InlineKeyboardButton(TTS+"TTS", callback_data="TTS"))

    return langs_inline

