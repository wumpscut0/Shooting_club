from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    input_text_to_admin = State()

    input_text_bullets = State()