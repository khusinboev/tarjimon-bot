from aiogram.dispatcher.filters.state import State, StatesGroup


class From(StatesGroup):
    channelAdd = State()
    channelDelete = State()
    send_msg = State()
    forward_msg = State()
    clear_msg = State()
