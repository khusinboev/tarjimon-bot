from aiogram.types import CallbackQuery
from aiogram.utils import exceptions

from config import dp, sql, db, adminPanel


class functions:
    @staticmethod
    async def check_on_start(user_id):
        sql.execute("SELECT chat_id FROM public.mandatorys")
        rows = sql.fetchall()
        error_code = 0
        for row in rows:
            # print(row)
            # print(row[0])
            r = await dp.bot.get_chat_member(chat_id=row[0], user_id=user_id)
            if r.status in ['member', 'creator', 'admin'] or user_id in adminPanel:
                pass
            else:
                error_code = 1
        if error_code == 0:
            return True
        else:
            return False


class panel_func:
    @staticmethod
    async def channel_add(chat_id):
        sql.execute(f"INSERT INTO public.mandatorys( chat_id ) VALUES('{chat_id}');")
        db.commit()

    @staticmethod
    async def channel_delete(id):
        sql.execute(f'''DELETE FROM public.mandatorys WHERE chat_id = '{id}' ''')
        db.commit()

    @staticmethod
    async def channel_list():
        sql.execute("SELECT chat_id from public.mandatorys")
        str = ''
        for row in sql.fetchall():
            chat_id = row[0]
            try:
                all_details = await dp.bot.get_chat(chat_id=chat_id)
                title = all_details["title"]
                channel_id = all_details["id"]
                info = all_details["description"]
                str += f"------------------------------------------------\nKanal useri: > {chat_id}\nKamal nomi: > {title}\nKanal id si: > {channel_id}\nKanal haqida: > {info}\n"
            except:
                str += "Kanalni admin qiling"
        return str


async def forward_send_msg(chat_id: int, from_chat_id: int, message_id: int) -> int:
    try:
        await dp.bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
        return 1
    except exceptions.BotBlocked:
        pass
    except exceptions.ChatNotFound:
        pass
    except exceptions.UserDeactivated:
        pass
    except exceptions.TelegramAPIError:
        pass
    except Exception as e:
        print(e)
    return 0


async def send_message_chats(chat_id: int, from_chat_id: int, message_id: int) -> int:
    try:
        await dp.bot.copy_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
        return 1
    except exceptions.BotBlocked:
        pass
    except exceptions.ChatNotFound:
        pass
    except exceptions.UserDeactivated:
        pass
    except exceptions.TelegramAPIError:
        pass
    except Exception as e:
        print(e)
    return 0


async def LangList():
    sql.execute(f"""select lang_in from public.langs_list""")
    lang_ins = sql.fetchall()
    lang_ins = [item[0] for item in lang_ins]

    sql.execute(f"""select lang_out from public.langs_list""")
    lang_outs = sql.fetchall()
    lang_outs = [item[0] for item in lang_outs]

    return lang_ins, lang_outs


async def UserLangs(user_id):
    sql.execute(f"""select lang_in from public.langs_list where code=(
    select in_lang from public.user_langs where user_id={user_id})""")
    user_in = sql.fetchone()[0]

    sql.execute(f"""select lang_out from public.langs_list where code=(
    select out_lang from public.user_langs where user_id={user_id})""")
    user_out = sql.fetchone()[0]

    return user_in, user_out


async def Group_Lang(chat_id):
    sql.execute(f"""select lang_in from public.langs_list where code=(
    select in_lang from public.group_langs where chat_id={chat_id})""")
    chat_in = sql.fetchone()[0]

    sql.execute(f"""select lang_out from public.langs_list where code=(
    select out_lang from public.group_langs where chat_id={chat_id})""")
    chat_out = sql.fetchone()[0]

    return chat_in, chat_out


async def UserCheckLang(call: CallbackQuery):
    user_id = call.from_user.id
    if ' ' in call.data:
        sql.execute(f"""select code from public.langs_list where lang_out='{call.data}'""")
        code = sql.fetchone()[0]

        sql.execute(f"""UPDATE public.user_langs SET out_lang = '{code}' WHERE user_id='{user_id}'""")
        db.commit()
    elif call.data == 'TTS':
        sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
        tts = sql.fetchone()[0]
        sql.execute(f"""UPDATE public.users_tts SET tts = {not tts} WHERE user_id='{user_id}'""")
        db.commit()
    else:
        sql.execute(f"""select code from public.langs_list where lang_in='{call.data}'""")
        code = sql.fetchone()[0]
        sql.execute(f"""UPDATE public.user_langs SET in_lang = '{code}' WHERE user_id='{user_id}'""")
        db.commit()


async def GroupCheckLang(call: CallbackQuery):
    chat_id = call.message.chat.id
    if ' ' in call.data:
        sql.execute(f"""select code from public.langs_list where lang_out='{call.data}'""")
        code = sql.fetchone()[0]

        sql.execute(f"""UPDATE public.group_langs SET out_lang = '{code}' WHERE chat_id='{chat_id}'""")
        db.commit()
    else:
        sql.execute(f"""select code from public.langs_list where lang_in='{call.data}'""")
        code = sql.fetchone()[0]
        sql.execute(f"""UPDATE public.group_langs SET in_lang = '{code}' WHERE chat_id='{chat_id}'""")
        db.commit()
