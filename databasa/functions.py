import datetime
import pytz

from config import sql, db


async def CreateBasa():
    sql.execute("""CREATE TABLE IF NOT EXISTS public.accounts
(
    id SERIAL NOT NULL,
    user_id bigint NOT NULL,
    username character varying(32),
    lang_code character varying(10),
    CONSTRAINT accounts_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.channels
(
    id SERIAL NOT NULL,
    chat_id bigint NOT NULL,
    title character varying,
    username character varying,
    types character varying,
    CONSTRAINT channels_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.groups
(
    id SERIAL NOT NULL,
    chat_id bigint NOT NULL,
    title character varying,
    username character varying,
    types character varying,
    CONSTRAINT groups_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.mandatorys
(
    id SERIAL NOT NULL,
    chat_id character varying NOT NULL,
    CONSTRAINT mandatorys_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.user_langs
(
    user_id bigint NOT NULL,
    in_lang character varying(25) NOT NULL DEFAULT 'uz',
    out_lang character varying(25) NOT NULL DEFAULT 'en',
    CONSTRAINT user_langs_pkey PRIMARY KEY (user_id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.users_status
(
    user_id bigint NOT NULL,
    date date NOT NULL,
    active_date date,
    CONSTRAINT users_status_pkey PRIMARY KEY (user_id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.users_tts
(
    user_id bigint NOT NULL,
    tts boolean NOT NULL DEFAULT false,
    CONSTRAINT users_tts_pkey PRIMARY KEY (user_id)
)""")
    db.commit()

    sql.execute("""
CREATE OR REPLACE FUNCTION public.user_lang()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
begin
	insert into user_langs( user_id, in_lang, out_lang )
	values( new.user_id, 'uz', 'en' );
	return null;
end
$BODY$;
ALTER FUNCTION public.user_lang()
    OWNER TO postgres;""")
    db.commit()

    sql.execute("""CREATE OR REPLACE FUNCTION public.user_status()
                        RETURNS trigger
                        LANGUAGE 'plpgsql'
                        COST 100
                        VOLATILE NOT LEAKPROOF
                    AS $BODY$
                    begin
                        insert into users_status( user_id, date, active_date )
                        values( new.user_id, date( current_date at time zone 'Asia/Tashkent' ), date( current_date at time zone 'Asia/Tashkent' ) );
                        return null;
                    end
                    $BODY$;
                    ALTER FUNCTION public.user_status()
                        OWNER TO postgres;""")
    db.commit()

    sql.execute("""
CREATE OR REPLACE FUNCTION public.user_tts()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
begin
	insert into users_tts( user_id, tts )
	values( new.user_id, 'false' );
	return Null;
end
$BODY$;

ALTER FUNCTION public.user_tts()
    OWNER TO postgres;""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER user_lang
    AFTER INSERT
    ON public.accounts
    FOR EACH ROW
    EXECUTE FUNCTION public.user_lang();""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER user_status
    AFTER INSERT
    ON public.accounts
    FOR EACH ROW
    EXECUTE FUNCTION public.user_status();""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER user_tts
    AFTER INSERT
    ON public.accounts
    REFERENCING NEW TABLE AS new
    FOR EACH ROW
    EXECUTE FUNCTION public.user_tts();""")
    db.commit()


async def Auth_Function(message):
    user_id = message.from_user.id
    username = message.from_user.username
    lang_code = message.from_user.language_code

    sql.execute(f"""SELECT user_id FROM accounts WHERE user_id = {user_id}""")
    check = sql.fetchone()
    if check == None:
        sana = datetime.datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%d-%m-%Y %H:%M')
        sql.execute(
            f"""INSERT INTO accounts (user_id, username, lang_code) VALUES ('{user_id}', '{username}', '{lang_code}')""")
        db.commit()
