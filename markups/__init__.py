from aiogram.filters.callback_data import CallbackData

from bot.FSM import States
from markups.core import InitializeMarkupInterface, TextWidget, ButtonWidget

from tools.emoji import Emoji


class Info(InitializeMarkupInterface):
    def __init__(
        self,
        text: str,
        ok_text: str = "Ok",
        back_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__()
        self.info = TextWidget(text=text)
        self.ok = ButtonWidget(text=ok_text, callback_data=back_callback_data)

        self.text_message_markup.add_text_row(self.info)
        self.text_message_markup.add_button_in_last_row(self.ok)


class Temp(InitializeMarkupInterface):
    def __init__(
        self,
        text: str = f"{Emoji.HOURGLASS_START} Processing...",
        state: States | None = None,
    ):
        super().__init__(state)
        self.temp = TextWidget(text=text)

        self.text_message_markup.add_text_row(self.temp)


class Back(InitializeMarkupInterface):
    def __init__(
        self,
        *,
        text: str = f"{Emoji.BACK} Back",
        callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__()
        self.back = ButtonWidget(text=text, callback_data=callback_data)

        self.text_message_markup.add_button_in_new_row(self.back)


class LeftRight(InitializeMarkupInterface):
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

        self.text_message_markup.add_buttons_in_new_row(self.left, self.right)


class LeftBackRight(InitializeMarkupInterface):
    def __init__(
        self,
        left_callback_data: str | CallbackData,
        right_callback_data: str | CallbackData,
        *,
        left_text: str = f"{Emoji.LEFT}",
        right_text: str = f"{Emoji.RIGHT}",
        left_mark: str = "",
        right_mark: str = "",
        back_text: str = f"{Emoji.BACK} Back",
        back_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__()
        self.left_right = LeftRight(
            left_callback_data=left_callback_data,
            right_callback_data=right_callback_data,
            left_text=left_text,
            right_text=right_text,
            left_mark=left_mark,
            right_mark=right_mark,
        )
        self.back = Back(text=back_text, callback_data=back_callback_data)

        self.text_message_markup.add_buttons_in_new_row(
            self.left_right.left,
            self.back.back,
            self.left_right.right,
        )


class Input(InitializeMarkupInterface):
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
        self.back = Back(text=back_text, callback_data=back_callback_data)

        self.text_message_markup.add_text_row(self.info)
        self.text_message_markup.attach(self.back)


class Conform(InitializeMarkupInterface):
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
        self.yes = ButtonWidget(text=yes_text, callback_data=yes_callback_data)
        self.no = Back(text=no_text, callback_data=no_callback_data)

        self.text_message_markup.add_text_row(TextWidget(text=text))
        self.text_message_markup.add_buttons_in_new_row(self.yes, self.no.back)


class ErrorInfo(InitializeMarkupInterface):
    def __init__(
        self,
        text: str = f"Error during data loading {Emoji.CRYING_CAT + Emoji.BROKEN_HEARTH} Sorry",
        back_callback_data: str | CallbackData = "return_to_context",
    ):
        super().__init__()
        self.text_message_markup.attach(Info(text, back_callback_data=back_callback_data))
