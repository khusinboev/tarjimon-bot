import asyncio
from asyncio import exceptions
from aiogram import types
from aiogram.types import CallbackQuery, ChatActions, InlineKeyboardButton
from deep_translator import GoogleTranslator
from gtts import gTTS
from aiogram.utils import exceptions
from buttons.mButtons import JoinBtn, LangsInline
from config import dp, bot, adminPanel, sql, adminStart, db
from databasa.functions import Auth_Function
from function.functions import functions, UserCheckLang
from PIL import Image
import pytesseract


@dp.message_handler(commands='lang', chat_type=types.ChatType.PRIVATE)
async def change_lang(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
    await Auth_Function(message)
    await message.answer("Choose languages", reply_markup=await LangsInline(message.from_user.id))


@dp.message_handler(commands='help', chat_type=types.ChatType.PRIVATE)
async def change_lang(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.UPLOAD_VIDEO)
    await Auth_Function(message)
    await message.answer_video(video=open('video/useBot.mp4', 'rb'),
                               caption="Botdan foydalanish uchun qo'llanma/Manual for using the bot\n\n\n"
                                       "For help admin: @coder_admin_py")


@dp.message_handler(content_types="text", chat_type=types.ChatType.PRIVATE)
async def translator(message: types.Message):
    exchangeLang = types.InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄Exchange Languages", callback_data="exchangeLang"))
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
    await Auth_Function(message)
    user_id = message.from_user.id
    try:
        if await functions.check_on_start(message.chat.id) or user_id in adminPanel:

            lang_in, lang_out, trText = await text_translate(text=message.text, user_id=user_id)

            sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
            tts = sql.fetchone()[0]
            if trText is None:
                await message.answer(text=message.text, reply_markup=exchangeLang)
            elif len(trText) < 4096:
                if tts:
                    try:
                        tts = gTTS(text=trText, lang=lang_out)
                        tts.save(f'Audios/{user_id}.mp3')

                        await message.answer_audio(audio=open(f'Audios/{user_id}.mp3', 'rb'),
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

                    await message.answer_audio(audio=open(f'Audios/{user_id}.mp3', 'rb'),
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

    else:
        print(call.data)
        await dp.bot.send_message(chat_id=adminStart,
                                  text=f"Error in call query: \n\n{call.data}\n\n\n{call.from_user}")


@dp.message_handler(content_types=types.ContentType.PHOTO, chat_type=types.ChatType.PRIVATE)
async def photo_tr_jpg(message: types.Message):
    exchangeLang = types.InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄Exchange Languages", callback_data="exchangeLang"))
    await Auth_Function(message)
    user_id = message.from_user.id
    try:
        if await functions.check_on_start(message.chat.id) or user_id in adminPanel:
            await message.answer("Waiting...")
            await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
            file_name = f"photos/{message.from_user.id}.jpg"
            photo = message.photo[-1]
            photo_file = await photo.get_file()
            await photo_file.download(destination_file=file_name)

            # pytesseract.pytesseract.tesseract_cmd = r'D:\Programs\tesserract\tesseract.exe'

            # Rasmni ochish
            image = Image.open(file_name)
            lang_tx = '''uzb+tur+tgk+eng+jpn+ita+rus+kor+ara+chi_sim+fra+deu+hin+aze+dar+kaz+tkm+kir+amh+ind'''
            # Rasmni OCR bilan o'qish
            text = pytesseract.image_to_string(image, lang=lang_tx)
            lang_in, lang_out, trText = await text_translate(text=text, user_id=user_id)

            sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
            tts = sql.fetchone()[0]
            if trText is None:
                await message.answer(text="None", reply_markup=exchangeLang)
            elif len(trText) < 4096:
                if tts:
                    try:
                        tts = gTTS(text=trText, lang=lang_out)
                        tts.save(f'Audios/{user_id}.mp3')

                        await message.answer_audio(audio=open(f'Audios/{user_id}.mp3', 'rb'),
                                                   caption=f"<code>{trText}</code>", parse_mode="html",
                                                   reply_markup=exchangeLang)
                    except:
                        await message.answer(text=f"<code>{trText}</code>", parse_mode="html", reply_markup=exchangeLang)
                else:
                    await message.answer(text=f"<code>{trText}</code>", parse_mode="html", reply_markup=exchangeLang)
            else:
                num = trText.split()
                fT = " ".join(num[:(len(num) // 2)])
                tT = " ".join(num[(len(num) // 2):])
                try:
                    tts = gTTS(text=trText, lang=lang_out)
                    tts.save(f'Audios/{user_id}.mp3')

                    await message.answer_audio(audio=open(f'Audios/{user_id}.mp3', 'rb'),
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
        await dp.bot.send_message(chat_id=adminStart, text=f"Error in translation: \n\n{ex}\n\n\n{message.from_user}")
        await message.answer(text="Error. Check the your message and resend me")

    # loop = asyncio.get_running_loop()
    # loop.run_in_executor(None, lambda: asyncio.run(photo_tr(image_path=file_name,
    #                                                         user_id=message.from_user.id,
    #                                                         message=message)))


async def text_translate(text, user_id):
    sql.execute(f"""select in_lang from public.user_langs where user_id={user_id}""")
    lang_in = sql.fetchone()[0]

    sql.execute(f"""select out_lang from public.user_langs where user_id={user_id}""")
    lang_out = sql.fetchone()[0]

    translator = GoogleTranslator(source=lang_in, target=lang_out)
    trText = str(translator.translate(text))

    return lang_in, lang_out, trText


# async def photo_tr(image_path, user_id, message: types.Message):
#     sql.execute(f"""select in_lang from public.user_langs where user_id={user_id}""")
#     lang_in = sql.fetchone()[0]
#     sql.execute(f"""select out_lang from public.user_langs where user_id={user_id}""")
#     lang_out = sql.fetchone()[0]
#     translater = GoogleTranslator(source=lang_in, target=lang_out)
#
#     img = cv2.imread(image_path)
#     reader = easyocr.Reader([lang_in], gpu=False)
#     text_ = reader.readtext(img)
#     threshold = 0.25
#     texts = ''
#     res = True
#     for t_, t in enumerate(text_):
#         bbox, text, score = t
#
#         if score > threshold:
#             texts += f"{text}\n"
#
#     res_text = "None"
#     if res:
#         plt.imsave(image_path, img)
#         if len(texts) > 2:
#             if lang_in == lang_out:
#                 res_text = texts
#             else:
#                 res_text = translater.translate(texts)
#
#     else:
#         if len(texts) > 2:
#             if lang_in == lang_out:
#                 res_text = texts
#             else:
#                 res_text = translater.translate(texts)
#
#     url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
#     response = requests.post(url, data={'chat_id': user_id, 'text': res_text})
#     content = response.content.decode("utf8")
#     json.loads(content)


# @dp.message_handler(content_types=types.ContentType.DOCUMENT, chat_type=types.ChatType.PRIVATE)
# async def photo_tr_other(message: types.Message):
#     pass
#     await message.answer("Waiting...")
#     await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.UPLOAD_PHOTO)
#     document = message.document
#     file_name = f"photos/{message.from_user.id}.png"
#     document_file = await document.get_file()
#     await document_file.download(destination_file=file_name)
#
#     loop = asyncio.get_running_loop()
#     loop.run_in_executor(None, lambda: asyncio.run(photo_tr(image_path=file_name,
#                                                             user_id=message.from_user.id,
#                                                             message=message)))
#
#
