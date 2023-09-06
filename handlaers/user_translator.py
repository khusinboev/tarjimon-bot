from aiogram import types
from aiogram.types import CallbackQuery
from deep_translator import GoogleTranslator
from gtts import gTTS

from buttons.mButtons import JoinBtn, LangsInline
from config import dp, adminStart, sql
from databasa.functions import Auth_Function
from function.functions import functions, UserCheckLang


@dp.message_handler(commands='lang', chat_type=types.ChatType.PRIVATE)
async def change_lang(message: types.Message):
    await message.answer("Choose languages", reply_markup=await LangsInline(message.from_user.id))


@dp.message_handler(commands='help', chat_type=types.ChatType.PRIVATE)
async def change_lang(message: types.Message):
    await message.answer_video(video=open('video/useBot.mp4', 'rb'),
                               caption="Botdan foydalanish uchun qo'llanma/Manual for using the bot\n\n\nFor help admin: @coder_admin_py")


@dp.message_handler(content_types="text", chat_type=types.ChatType.PRIVATE)
async def translator(message: types.Message):
    await Auth_Function(message)
    user_id = message.from_user.id

    if await functions.check_on_start(message.chat.id) or user_id in adminStart:

        sql.execute(f"""select in_lang from public.user_langs where user_id={user_id}""")
        lang_in = sql.fetchone()[0]

        sql.execute(f"""select out_lang from public.user_langs where user_id={user_id}""")
        lang_out = sql.fetchone()[0]

        sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
        tts = sql.fetchone()[0]

        translator = GoogleTranslator(source=lang_in, target=lang_out)
        trText = translator.translate(message.text)

        if tts:
            try:
                tts = gTTS(text=trText, lang=lang_out)
                tts.save(f'Audios/{user_id}.mp3')

                await message.answer_audio(audio=open(f'Audios/{user_id}.mp3', 'rb'),
                                           caption=f"Tarjimasi: 👇\n\n<code>{trText}</code>", parse_mode="html")
            except:
                await message.answer(text=f"<code>{trText}</code>", parse_mode="html")
        else:
            await message.answer(text=f"<code>{trText}</code>", parse_mode="html")

    else:
        await message.answer(
            "Botimizdan foydalanish uchun kanalimizga azo bo'ling\nSubscribe to our channel to use our bot",
            reply_markup=await JoinBtn(user_id))


def CallFilter():
    sql.execute(f"""select lang_in from public.langs_list""")
    lang_ins = sql.fetchall()
    lang_ins = [item[0] for item in lang_ins]

    sql.execute(f"""select lang_out from public.langs_list""")
    lang_outs = sql.fetchall()
    lang_outs = [item[0] for item in lang_outs]
    lang_outs.append("TTS")

    alllist = lang_ins + lang_outs
    return alllist


@dp.callback_query_handler(text=CallFilter(), chat_type=types.ChatType.PRIVATE)
async def check(call: CallbackQuery):
    await call.answer()
    await UserCheckLang(call)
    try:
        await call.message.edit_reply_markup(await LangsInline(call.from_user.id))
    except:
        pass
