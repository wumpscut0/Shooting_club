from aiogram.filters.callback_data import CallbackData

from markups.core import KeyboardMarkupConstructor, ButtonWidget
from tools import Emoji


class LeftRight(KeyboardMarkupConstructor):
    def __init__(
        self,
        left_callback_data: str | CallbackData,
        right_callback_data: str | CallbackData,
        *,
        left_text: str = f"{Emoji.LEFT}",
        right_text: str = f"{Emoji.RIGHT}",
        left_mark: str = "",
        right_mark: str = "",
    ):
        super().__init__()
        self.left = ButtonWidget(
            text=left_text, mark=left_mark, sep="", callback_data=left_callback_data
        )
        self.right = ButtonWidget(
            text=right_text,
            mark=right_mark,
            mark_left=False,
            sep="",
            callback_data=right_callback_data,
        )

        self.add_buttons_in_new_row(self.left, self.right)


class LeftBackRight(LeftRight):
    def __init__(
        self,
        left_callback_data: str | CallbackData,
        right_callback_data: str | CallbackData,
        *,
        left_text: str = f"{Emoji.LEFT}",
        right_text: str = f"{Emoji.RIGHT}",
        left_mark: str = "",
        right_mark: str = "",
        back_text: str = f"{Emoji.BACK}",
        back_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__(
            left_callback_data=left_callback_data,
            right_callback_data=right_callback_data,
            left_text=left_text,
            right_text=right_text,
            left_mark=left_mark,
            right_mark=right_mark,
        )

        self.back = ButtonWidget(text=back_text, callback_data=back_callback_data)

        self.add_buttons_in_new_row(
            self.left,
            self.back,
            self.right,
        )
