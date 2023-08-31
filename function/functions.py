from aiogram.utils import exceptions

from config import dp, sql, db


class functions:
    @staticmethod
    async def check_on_start(user_id):
        sql.execute("SELECT chat_id FROM public.mandatorys")
        rows = sql.fetchall()
        error_code = 0
        for row in rows:
            r = await dp.bot.get_chat_member(chat_id=row[0], user_id=user_id)
            if r.status in ['member', 'creator', 'admin']:
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


async def forward_send_msg(chat_id: int, from_chat_id: int, message_id: int) -> bool:
    try:
        await dp.bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
    except exceptions.BotBlocked:
        pass
    except exceptions.ChatNotFound:
        pass
    except exceptions.UserDeactivated:
        pass
    except exceptions.TelegramAPIError:
        pass
    else:
        return True
    return False


async def send_message_chats(chat_id: int, from_chat_id: int, message_id: int) -> bool:
    try:
        await dp.bot.copy_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
    except exceptions.BotBlocked:
        pass
    except exceptions.ChatNotFound:
        pass
    except exceptions.UserDeactivated:
        pass
    except exceptions.TelegramAPIError:
        pass
    else:
        return True
    return False


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