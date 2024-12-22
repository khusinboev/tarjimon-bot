from asyncio import exceptions
from aiogram import types
from aiogram.types import CallbackQuery, ChatActions, InlineKeyboardButton, ParseMode, WebAppInfo, InlineKeyboardMarkup
from deep_translator import GoogleTranslator
from gtts import gTTS
from aiogram.utils import exceptions
from buttons.mButtons import JoinBtn, LangsInline
from config import dp, bot, adminPanel, sql, adminStart, db, TOKEN
from databasa.functions import Auth_Function
from function.functions import functions, UserCheckLang
from PIL import Image
from pydub import AudioSegment
import speech_recognition as sr
import platform, threading, io, asyncio, os#, pytesseract


def text_translate(text, user_id):
    sql.execute(f"""select in_lang from public.user_langs where user_id={user_id}""")
    lang_in = sql.fetchone()[0]

    sql.execute(f"""select out_lang from public.user_langs where user_id={user_id}""")
    lang_out = sql.fetchone()[0]

    translator = GoogleTranslator(source=lang_in, target=lang_out)
    trText = str(translator.translate(text))
    return lang_in, lang_out, trText


@dp.message_handler(commands="from", chat_type=types.ChatType.PRIVATE, user_id=adminPanel)
async def welcome(message: types.Message):
    user_id = message.text[6:]
    if user_id.isdigit():
        sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{user_id}'")
        db.commit()
        sql.execute(f"DELETE FROM public.user_langs WHERE user_id ='{user_id}'")
        db.commit()
        sql.execute(f"DELETE FROM public.users_status WHERE user_id ='{user_id}'")
        db.commit()
        sql.execute(f"DELETE FROM public.users_tts WHERE user_id ='{user_id}'")
        db.commit()
        await message.answer(f"o'chirildi, {user_id}")
    else:
        await message.answer("xato")


@dp.message_handler(commands='lang', chat_type=types.ChatType.PRIVATE)
async def change_lang(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
    await Auth_Function(message)
    await message.answer("Choose languages", reply_markup=await LangsInline(message.from_user.id))


@dp.message_handler(commands='help', chat_type=types.ChatType.PRIVATE)
async def change_lang(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.UPLOAD_VIDEO)
    await Auth_Function(message)
    await message.answer_video(video=open( 'video/useBot.mp4', 'rb'),
                               caption="Botdan foydalanish uchun qo'llanma/Manual for using the bot\n\n\n"
                                       "For help admin: @adkhambek_4")


@dp.message_handler(content_types="text", chat_type=types.ChatType.PRIVATE)
async def translator(message: types.Message):
    exchangeLang = types.InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄Exchange Languages", callback_data="exchangeLang"),
        InlineKeyboardButton(text="👅Langs", callback_data="lang_list"))

    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
    await Auth_Function(message)
    user_id = message.from_user.id
    try:
        if await functions.check_on_start(message.chat.id) or user_id in adminPanel:

            lang_in, lang_out, trText = text_translate(text=message.text, user_id=user_id)

            sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
            tts = sql.fetchone()[0]
            if trText is None:
                await message.answer(text=message.text, reply_markup=exchangeLang)
            elif len(trText) < 4096:
                if tts:
                    try:
                        tts = gTTS(text=trText, lang=lang_out)
                        tts.save( f'Audios/{user_id}.mp3')

                        await message.answer_audio(audio=open( f'Audios/{user_id}.mp3', 'rb'),
                                                   caption=f"<code>{trText}</code>", parse_mode="html",
                                                   reply_markup=exchangeLang)
                    except:
                        await message.answer(text=f"<code>{trText}</code>", parse_mode="html", reply_markup=exchangeLang)
                else:
                    await message.answer(text=f"<code>{trText}</code>", parse_mode="html", reply_markup=exchangeLang)
            else:
                num = trText.split()
                fT = " ".join(num[:(len(num)//2)])
                tT = " ".join(num[(len(num)//2):])
                try:
                    tts = gTTS(text=trText, lang=lang_out)
                    tts.save(f'Audios/{user_id}.mp3')

                    await message.answer_audio(audio=open( f'Audios/{user_id}.mp3', 'rb'),
                                               caption=f"<code>{fT}</code>", parse_mode="html",
                                               reply_markup=exchangeLang)
                    await message.answer(text=f"<code>{tT}</code>", parse_mode="html", reply_markup=exchangeLang)
                except:
                    await message.answer(text=f"<code>{fT}</code>", parse_mode="html", reply_markup=exchangeLang)
                    await message.answer(text=f"<code>{tT}</code>", parse_mode="html", reply_markup=exchangeLang)

        else:
            await message.answer(
                "Botimizdan foydalanish uchun kanalimizga azo bo'ling\nSubscribe to our channel to use our bot",
                reply_markup=await JoinBtn(user_id))
    except Exception as ex:
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await dp.bot.send_message(chat_id=adminStart, text=f"Error in translation: \n\n{ex}\n\n\n{message.from_user}")


def CallFilter(all):
    print(all)
    sql.execute(f"""select lang_in from public.langs_list""")
    lang_ins = sql.fetchall()
    lang_ins = [item[0] for item in lang_ins]

    sql.execute(f"""select lang_out from public.langs_list""")
    lang_outs = sql.fetchall()
    lang_outs = [item[0] for item in lang_outs]
    lang_outs.append("TTS")

    return lang_ins + lang_outs


@dp.callback_query_handler(chat_type=types.ChatType.PRIVATE)
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    if call.data in CallFilter("all"):
        try:
            await call.answer()
        except exceptions.InvalidQueryID:
            pass
        await UserCheckLang(call)
        try:
            await call.message.edit_reply_markup(await LangsInline(user_id))
        except exceptions.MessageNotModified:
            pass
        except exceptions.MessageToEditNotFound:
            pass
        except exceptions.MessageIdInvalid:
            pass
        except Exception as e:
            await dp.bot.send_message(chat_id=adminStart, text=f"Error in edit: \n\n{e}\n\n\n{call.from_user}")
    elif call.data == "exchangeLang":
        sql.execute(f"""select in_lang, out_lang from public.user_langs where user_id='{user_id}'""")
        codes = sql.fetchall()[0]
        await call.answer(f"{codes[1]} --> {codes[0]}")
        sql.execute(f"""UPDATE public.user_langs SET out_lang = '{codes[0]}' WHERE user_id='{user_id}'""")
        db.commit()
        sql.execute(f"""UPDATE public.user_langs SET in_lang = '{codes[1]}' WHERE user_id='{user_id}'""")
        db.commit()
    elif call.data == "lang_list":
        await call.answer()
        await bot.send_chat_action(chat_id=call.message.from_user.id, action=ChatActions.TYPING)
        await Auth_Function(call.message)
        await call.message.answer("Choose languages", reply_markup=await LangsInline(call.message.from_user.id))
    else:
        print(call.data)
        await dp.bot.send_message(chat_id=adminStart,
                                  text=f"Error in call query: \n\n{call.data}\n\n\n{call.from_user}")


@dp.message_handler(content_types=types.ContentType.PHOTO, chat_type=types.ChatType.PRIVATE)
async def photo_tr_jpg(message: types.Message):
    web_app_info = WebAppInfo(url="https://translate.google.com/?hl=en&tab=TT&sl=en&tl=uz&op=images")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="WEB", web_app=web_app_info))
    await message.answer("Try the WEB👇", reply_markup=keyboard)
    # user_id = message.from_user.id
    # from_us = message.from_user.as_json()
    # photo = message.photo[-1]
    # photo_file = io.BytesIO()
    # await photo.download(destination_file=photo_file)
    # photo_file.seek(0)
    # image = Image.open(photo_file)
    # grayscale_image = image.convert("L")
    # file_id = photo.file_unique_id
    # filename = f"photos/{file_id}.jpg"
    # with open(filename, 'wb') as output_file:
    #     grayscale_image.save(output_file, format="JPEG")
    #
    # await photo_tr(user_id, filename, from_us, message)


# async def photo_tr(user_id, file_name, from_user, message):
#     exchangeLang = types.InlineKeyboardMarkup().add(
#         InlineKeyboardButton("🔄Exchange Languages", callback_data="exchangeLang"),
#         InlineKeyboardButton(text="👅Langs", callback_data="lang_list"))
#     try:
#         if await functions.check_on_start(user_id) or user_id in adminPanel:
#             sent_message = await bot.send_message(chat_id=user_id, text="Waiting!...", reply_markup=exchangeLang)
#             if platform.system() == 'Windows':
#                 pytesseract.pytesseract.tesseract_cmd = r'D:\Programs\tesserract\tesseract.exe'
#
#             image = Image.open(file_name)
#             lang_tx = '''uzb+tur+tgk+eng+jpn+ita+rus+kor+ara+chi_sim+fra+deu+hin+aze+dar+kaz+tkm+kir+amh+ind'''
#
#             text = pytesseract.image_to_string(image, lang=lang_tx)
#             if text != '':
#                 lang_in, lang_out, trText = text_translate(text=text, user_id=user_id)
#                 if len(trText) < 4096:
#                     await bot.send_message(chat_id=user_id, text=str(trText), reply_markup=exchangeLang)
#                 else:
#                     num = trText.split()
#                     fT = " ".join(num[:(len(num) // 2)])
#                     tT = " ".join(num[(len(num) // 2):])
#                     await bot.send_message(chat_id=user_id, text=str(fT), reply_markup=exchangeLang)
#                     await bot.send_message(chat_id=user_id, text=str(tT), reply_markup=exchangeLang)
#             else:
#                 await bot.send_photo(chat_id=adminStart, photo=open(file_name, 'rb'), caption=from_user)
#             try:
#                 await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
#             except exceptions.MessageToDeleteNotFound:
#                 pass
#         else:
#             await bot.send_message(chat_id=user_id,
#                                    text="Botimizdan foydalanish uchun kanalimizga azo bo'ling\nSubscribe to our channel to use our bot",
#                                    reply_markup=await JoinBtn(user_id))
#     except Exception as ex:
#         await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
#         await bot.send_photo(chat_id=adminStart, photo=open(file_name, 'rb'),
#                              caption=f"Error in translation: \n\n{ex}\n\n\n{from_user}")
#         await bot.send_message(chat_id=user_id, text="Error. Check the your message and resend me",
#                                reply_markup=exchangeLang)


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.AUDIO], chat_type=types.ChatType.PRIVATE)
async def audio_tr(message: types.Message):
    # web_app_info = WebAppInfo(url="https://translate.google.com/?hl=en&sl=uz&tl=en&op=translate")
    # keyboard = InlineKeyboardMarkup()
    # keyboard.add(InlineKeyboardButton(text="WEB", web_app=web_app_info))
    # await message.answer("Try the WEB👇", reply_markup=keyboard)
    user_id = message.from_user.id
    sent_msg = await bot.send_message(chat_id=user_id,
                                      text="Bu jarayon ko'proq vaqt olishi mumkin, kuting...\nWaiting e few second...")
    if message.voice:
        file_id = message.voice.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_format = 'voice'
        file_name = message.voice.file_unique_id
    elif message.audio:
        file_id = message.audio.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_format = 'audio'
        file_name = message.audio.file_unique_id
    downloaded_file = await bot.download_file("audio_tr/"+file_path)
    temp_file_path = audio_tr + f'{file_name}.{file_format}'
    with open(temp_file_path, 'wb') as new_file:
        new_file.write(downloaded_file.read())
    if file_format == 'voice':
        audio = AudioSegment.from_ogg(temp_file_path)
    elif file_format == 'audio':
        print(temp_file_path)
        audio = AudioSegment.from_file(temp_file_path)

    audio_name =  f'audio_tr/{file_name}.wav'
    audio.export(audio_name, format='wav')
    os.remove(temp_file_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_name) as source:
        audio1 = recognizer.record(source)
    sql.execute(f"""select in_lang from public.user_langs where user_id={user_id}""")
    lang_in = sql.fetchone()[0]
    exchangeLang = types.InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄Exchange Languages", callback_data="exchangeLang"),
        InlineKeyboardButton(text="👅Langs", callback_data="lang_list"))
    try:
        text = recognizer.recognize_google(audio1, language=lang_in)
        # while True:
        #     res_text = ''
        #     if len(text) > 4090:
        #         r1, r2 = 0, 0
        #         num = text.split()
        #         for n in num:
        #             res_text += n
        #             r1 += len(n)
        #             r2 += 1
        #             if r1 > 4000:
        #                 break
        #         text = " ".join(num[:r2])
        #         await bot.send_message(chat_id=user_id, text=f"<code>{res_text}</code>", parse_mode='html')
        #     else:
        # await bot.send_message(chat_id=user_id, text=f"<code>{text}</code>", parse_mode='html', reply_markup=exchangeLang)
                # break

        lang_in, lang_out, trText = text_translate(text=text, user_id=user_id)
        await bot.send_message(chat_id=user_id, text=f"<code>{trText}</code>", parse_mode='html',
                               reply_markup=exchangeLang)
        await bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
    except Exception as ex:
        await bot.send_message(chat_id=user_id, text="Audio tushunarsiz!\n\nThe audio is unclear")
        await bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=adminStart,
                               text=f"Error text: \n\n<code>{ex}</code>\n\n\n{message.chat}",
                               parse_mode='html')
