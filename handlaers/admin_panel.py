from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, ReplyKeyboardMarkup, ChatActions
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, MigrateToChat, \
    TelegramAPIError

from Statess.statess import From
from buttons.mButtons import channel_btn, main_btn, reklama_btn
from config import dp, bot, sql, db, adminPanel
from function.functions import panel_func, forward_send_msg, send_message_chats


@dp.message_handler(commands=["developer", 'coder', 'programmer'], chat_type=types.ChatType.PRIVATE)
async def coder(msg: types.Message):
    await bot.send_chat_action(chat_id=msg.from_user.id, action=ChatActions.TYPING)
    await msg.reply("Bot dasturchisi @coder_admin_py\n\nPowered by @coder_admin_py", parse_mode='html')


markup = ReplyKeyboardMarkup(resize_keyboard=True)
markup.add("🔙Orqaga qaytish")


@dp.message_handler(commands=['admin', 'panel'], user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def new(msg: types.Message):
    await msg.answer("Assalomu alaykum admin janoblari", reply_markup=main_btn)


# await From.teststate.set()   state=From.teststate,

@dp.message_handler(text="🔙Orqaga qaytish", user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def backs(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatActions.TYPING)
    await message.reply("Bosh menyu", reply_markup=main_btn)


#          STATISTIKA            """"""""""""""""""""""

@dp.message_handler(text="📊Statistika", user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def new(msg: types.Message):
    sql.execute("SELECT COUNT(*) FROM accounts")
    followersall = sql.fetchone()[0]
    await msg.answer(
        f"👥Botdagi jami azolar soni: > {followersall}")


#           KANALLAR              """""""""""""""""""""

@dp.message_handler(text='🔧Kanallar', user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def new(msg: types.Message):
    await msg.answer("Tanlang", reply_markup=channel_btn)


@dp.message_handler(state=[From.channelDelete, From.channelAdd], text="🔙Orqaga qaytish", user_id=adminPanel,
                    chat_type=types.ChatType.PRIVATE)
async def backs(message: types.Message, state: FSMContext):
    await message.reply("Orqaga qaytildi", reply_markup=channel_btn)
    await state.finish()


@dp.message_handler(text="➕Kanal qo'shish", user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def channel_add(message: types.Message):
    await message.reply("Kanal qo'shish uchun kanalning userini yuboring.\nMisol uchun @coder_admin",
                        reply_markup=markup)
    await From.channelAdd.set()


@dp.message_handler(state=From.channelAdd, user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def channelAdd1(message: types.Message, state: FSMContext):
    channel_id = message.text.upper()
    sql.execute(f"SELECT chat_id FROM public.mandatorys WHERE chat_id = '{message.text.upper()}'")
    data = sql.fetchone()
    if data is None:
        if message.text[0] == '@':
            await panel_func.channel_add(channel_id)
            await state.finish()
            await message.reply("Kanal qo'shildi🎉🎉", reply_markup=channel_btn)
        else:
            await message.reply("Kanal useri xato kiritildi\nIltimos userni @coder_admin ko'rinishida kiriting",
                                reply_markup=channel_btn)
    else:
        await message.reply("Bu kanal avvaldan bor", reply_markup=channel_btn)
    await state.finish()


@dp.message_handler(text="❌Kanalni olib tashlash", user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def channelD(message: types.Message):
    await message.reply("O'chiriladigan kanalning userini yuboring.\nMisol uchun @coder_admin", reply_markup=markup)
    await From.channelDelete.set()


@dp.message_handler(state=From.channelDelete, user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def ChannelDel(message: types.Message, state: FSMContext):
    channel_id = message.text.upper()
    sql.execute(f"""SELECT chat_id FROM public.mandatorys WHERE chat_id = '{channel_id}'""")
    data = sql.fetchone()

    if data is None:
        await message.reply("Bunday kanal yo'q", reply_markup=channel_btn)
    else:
        if message.text[0] == '@':
            await panel_func.channel_delete(channel_id)
            await state.finish()
            await message.reply("Kanal muvaffaqiyatli o'chirildi", reply_markup=channel_btn)
        else:
            await message.reply("Kanal useri xato kiritildi\nIltimos userni @coder_admin ko'rinishida kiriting",
                                reply_markup=channel_btn)

    await state.finish()


@dp.message_handler(text="📋 Kanallar ro'yxati", chat_type=types.ChatType.PRIVATE)
async def channelList(message: types.Message):
    if len(await panel_func.channel_list()) > 3:
        await message.reply(await panel_func.channel_list())
    else:
        await message.reply("Hozircha kanallar yo'q")


#            REKLAMA          """"""""""""""""""""""#################


@dp.message_handler(text="📤Reklama", user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def all_send(message: types.Message):
    await message.reply("Foydalanuvchilarga xabar yuborish bo'limi", reply_markup=reklama_btn)


@dp.message_handler(state=[From.forward_msg, From.send_msg], text="🔙Orqaga qaytish", content_types=ContentType.ANY,
                    user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def all_users2(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Orqaga qaytildi", reply_markup=reklama_btn)


@dp.message_handler(lambda message: message.text == "📨Forward xabar yuborish", user_id=adminPanel,
                    chat_type=types.ChatType.PRIVATE)
async def all_users(message: types.Message, state: FSMContext):
    await message.answer(text="Forward yuboriladigan xabarni yuboring",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("🔙Orqaga qaytish"))
    await From.forward_msg.set()


@dp.message_handler(state=From.forward_msg, content_types=ContentType.ANY,
                    user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def all_users2(message: types.Message, state: FSMContext):
    await state.finish()
    sql.execute(f"SELECT user_id FROM public.accounts ")
    rows = sql.fetchall()
    num = 0
    for row in rows:
        if await forward_send_msg(from_chat_id=message.chat.id, message_id=message.message_id, chat_id=row[0]):
            num += 1

    await message.answer(text=f"Xabar yuborish yakunlandi, xabaringiz {num} ta odamga yuborildi",
                         reply_markup=reklama_btn)


@dp.message_handler(lambda message: message.text == "📬Oddiy xabar yuborish", user_id=adminPanel,
                    chat_type=types.ChatType.PRIVATE)
async def all_users(message: types.Message, state: FSMContext):
    await message.answer(text="Yuborilishi kerak bo'lgan xabarni yuboring",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("🔙Orqaga qaytish"))
    await From.send_msg.set()


@dp.message_handler(state=From.send_msg, content_types=ContentType.ANY, user_id=adminPanel,
                    chat_type=types.ChatType.PRIVATE)
async def all_users2(message: types.Message, state: FSMContext):
    await state.finish()
    sql.execute(f"SELECT user_id FROM public.accounts ")
    rows = sql.fetchall()
    num = 0
    for row in rows:
        if await send_message_chats(from_chat_id=message.chat.id, message_id=message.message_id, chat_id=row[0]):
            num += 1

    await message.answer(text=f"Xabar yuborish yakunlandi, xabaringiz {num} ta odamga yuborildi",
                         reply_markup=reklama_btn)


#              Tozalash           """"""""""""""""""""""

@dp.message_handler(text="♻️ Tozalash", user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def clear(message: types.Message):
    await message.reply("Tozalash kodini kiriting: ", reply_markup=markup)
    await From.clear_msg.set()


@dp.message_handler(state=From.clear_msg, text="🔙Orqaga qaytish", content_types=ContentType.ANY, user_id=adminPanel,
                    chat_type=types.ChatType.PRIVATE)
async def all_users2(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Orqaga qaytildi", reply_markup=main_btn)


@dp.message_handler(state=From.clear_msg, user_id=adminPanel, chat_type=types.ChatType.PRIVATE)
async def clear1(message: types.Message, state: FSMContext):
    if message.text == '0000':
        sql.execute("SELECT COUNT(*) FROM public.accounts")
        followers = sql.fetchone()[0]
        check_time = followers / 60 / 10
        text = ("Tozalash boshlandi\nTomom bo'linchaya {} daqiqa bor\n{} ta odam tekshiriladi\n\n"
                "Tozalash tamom bo'lincha hech novino tegmang❗️")
        text = text.format(check_time, followers)
        await message.reply(text)

        sql.execute(f"SELECT user_id FROM public.accounts ")
        rows = sql.fetchall()
        for row in rows:
            id = row[0]
            try:
                await dp.bot.send_message(chat_id=id, text="thanks")
            except BotBlocked:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{id}'")
                db.commit()
            except ChatNotFound:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{id}'")
                db.commit()
            except RetryAfter:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{id}'")
                db.commit()
            except UserDeactivated:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{id}'")
                db.commit()
            except MigrateToChat:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{id}'")
                db.commit()
            except TelegramAPIError:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{id}'")
                db.commit()
        await message.answer("Tozalash yakunlandi  ✅", reply_markup=main_btn)
        await state.finish()
    else:
        await message.answer("Xavfsizlik kodi noto'g'ri", reply_markup=main_btn)
        await state.finish()
