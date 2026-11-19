from aiogram.fsm.state import State, StatesGroup


class RequestForm(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_description = State()
