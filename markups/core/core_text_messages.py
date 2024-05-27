from aiogram.filters.callback_data import CallbackData

from bot.FSM import States
from markups.core import TextMessageConstructor, TextWidget, ButtonWidget
from tools import Emoji


class Info(TextMessageConstructor):
    def __init__(
        self,
        text: str,
        ok_text: str = "Ok",
        back_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__()
        self.info = TextWidget(text=text)
        self.ok = ButtonWidget(text=ok_text, callback_data=back_callback_data)

    async def init(self):
        self.add_texts_rows(self.info)
        self.add_button_in_last_row(self.ok)
        return self


class ErrorInfo(Info):
    def __init__(
        self,
        text: str = f"Error during data loading {Emoji.CRYING_CAT + Emoji.BROKEN_HEARTH} Sorry",
        back_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__(text, back_callback_data)


class Temp(TextMessageConstructor):
    def __init__(
        self,
        text: str = f"{Emoji.HOURGLASS_START} Processing...",
        state: States | None = None,
    ):
        super().__init__(state)
        self.temp = TextWidget(text=text)

    async def init(self):
        self.add_texts_rows(self.temp)
        return self


class Input(TextMessageConstructor):
    def __init__(
        self,
        text: str,
        *,
        back_text: str = f"{Emoji.DENIAL} Cancel",
        back_callback_data: str | CallbackData = "return_to_context",
        state: States | None = None,
    ):
        super().__init__(state)
        self.info = TextWidget(text=text)
        self.back = ButtonWidget(text=back_text, callback_data=back_callback_data)

    async def init(self):
        self.add_texts_rows(self.info)
        self.add_button_in_new_row(self.back)
        return self


class Conform(TextMessageConstructor):
    def __init__(
        self,
        text: str,
        yes_callback_data: str | CallbackData,
        *,
        yes_text: str = f"{Emoji.OK} Yes",
        no_text: str = f"{Emoji.DENIAL} No",
        no_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__()
        self.info = TextWidget(text=text)
        self.yes = ButtonWidget(text=yes_text, callback_data=yes_callback_data)
        self.no = ButtonWidget(text=no_text, callback_data=no_callback_data)

    async def init(self):
        self.add_texts_rows(self.info)
        self.add_buttons_in_new_row(self.yes, self.no)
        return self
