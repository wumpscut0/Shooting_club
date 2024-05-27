import os.path
from typing import List, Self

from aiogram.types import FSInputFile
from aiogram.utils.formatting import as_list, Text, Bold, Italic
from aiogram.utils.keyboard import InlineKeyboardBuilder

from abc import abstractmethod, ABC

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State

from tools.emoji import Emoji


class TextWidget:
    def __init__(
        self,
        *,
        mark: str = "",
        text: str = Emoji.BAN,
        mark_left: bool = True,
        sep: str = " ",
    ):
        self.mark = mark
        self._text = text
        self.mark_left = mark_left
        self.sep = sep

    @property
    def text(self):
        if self.mark_left:
            # separator = '' if str(self._text).startswith(self.separator) else self.separator
            return Text(self.mark) + Text(self.sep) + Bold(self._text)
        # separator = '' if str(self._text).endswith(self.separator) else self.separator
        return Bold(self._text) + Text(self.sep) + Text(self.mark)

    @text.setter
    def text(self, text: str):
        self._text = text


class DataTextWidget(TextWidget):
    def __init__(
        self,
        *,
        mark: str = "",
        text: str = Emoji.BAN,
        data: str = Emoji.GREY_QUESTION,
        sep: str = ": ",
        end: str = "",
    ):
        super().__init__(
            mark=mark,
            text=text,
        )
        self.data = data
        self.sep_ = sep
        self.end = end

    @property
    def text(self):
        return super().text + Text(self.sep_) + Italic(self.data) + Italic(self.end)


class ButtonWidget:
    def __init__(
        self,
        *,
        mark: str = "",
        text: str = None,
        mark_left: bool = True,
        sep: str = " ",
        callback_data: str | CallbackData = Emoji.BAN,
    ):
        self.mark = mark
        self._text = text
        self.mark_left = mark_left
        self.sep = sep
        self.callback_data = callback_data

    @property
    def text(self):
        # separator = '' if str(self._text).startswith(' ') else ' '
        if self.mark_left:
            return self.mark + self.sep + self._text
        return self._text + self.sep + self.mark

    @text.setter
    def text(self, text: str):
        self._text = text


class TextMarkupConstructor:
    def __init__(self, map_: List[DataTextWidget | TextWidget] | None = None):
        super().__init__()
        self._text_map = [] if map_ is None else map_

    @property
    def text_map(self):
        return self._text_map

    @text_map.setter
    def text_map(self, map_: List[DataTextWidget | TextWidget]):
        self._text_map = map_

    def add_texts_rows(self, *args: DataTextWidget | TextWidget):
        for text in args:
            self._text_map.append(text)

    @property
    def text(self):
        if not self._text_map:
            return Emoji.BAN
        return (as_list(*[text.text for text in self._text_map])).as_html()


class KeyboardMarkupConstructor:
    """
    Max telegram inline keyboard buttons row is 8.
     add_button(s)_in_last_row will automatically move the button to the new row

     Max telegram inline keyboard buttons row is 4 with only emoji text in message.
     for this case toggle flag only_emoji_text=True

    """

    _limitation_row = 8
    _limitation_row_with_emoji = 4

    def __init__(self, map_: List[List[ButtonWidget]] | None = None):
        super().__init__()
        self._keyboard_map = [[]] if map_ is None else map_

    @property
    def keyboard_map(self):
        return self._keyboard_map

    @keyboard_map.setter
    def keyboard_map(self, map_: List[List[ButtonWidget]]):
        self._keyboard_map = map_

    def add_button_in_last_row(self, buttons: ButtonWidget, only_emoji_text=False):
        if only_emoji_text:
            limitations_row = self._limitation_row_with_emoji
        else:
            limitations_row = self._limitation_row

        if len(self._keyboard_map[-1]) == limitations_row:
            self.add_button_in_new_row(buttons)
        else:
            self._keyboard_map[-1].append(buttons)

    def add_buttons_in_last_row(self, *buttons: ButtonWidget, only_emoji_text=False):
        for button in buttons:
            self.add_button_in_last_row(button, only_emoji_text)

    def add_button_in_new_row(self, button: ButtonWidget):
        self._keyboard_map.append([button])

    def add_buttons_in_new_row(self, *buttons: ButtonWidget, only_emoji_text=False):
        if only_emoji_text:
            limitations_row = self._limitation_row_with_emoji
        else:
            limitations_row = self._limitation_row
        self._keyboard_map.append([])
        limit = 0
        for button in buttons:
            if limit == limitations_row:
                limit = 0
                self.add_button_in_new_row(button)
            else:
                self.add_button_in_last_row(button, only_emoji_text)
            limit += 1

    def add_buttons_as_column(self, *buttons: ButtonWidget):
        for button in buttons:
            self.add_button_in_new_row(button)

    @property
    def keyboard(self):
        if self._keyboard_map == [[]]:
            return

        markup = InlineKeyboardBuilder()
        for buttons_row in self._keyboard_map:
            row = InlineKeyboardBuilder()
            for button in buttons_row:
                row.button(text=button.text, callback_data=button.callback_data)
            markup.attach(row)
        return markup.as_markup()


class PhotoMarkupConstructor:

    def __init__(self, photo: str | FSInputFile | None = None):
        super().__init__()
        self._photo = photo

    @property
    def photo(self):
        if not self._photo:
            return FSInputFile("../../images/no_photo.jpg")
        return self._photo

    @photo.setter
    def photo(self, photo: str | FSInputFile):
        self._photo = photo


class VoiceMarkupConstructor:
    def __init__(self, voice: str | FSInputFile | None = None):
        super().__init__()
        self._voice = voice

    @property
    def voice(self):
        if self._voice is None:
            return FSInputFile(os.path.join(os.path.dirname(__file__), "..", "..", "audio", "no_audio"))
        return self._voice

    @voice.setter
    def voice(self, voice: str | FSInputFile):
        self._voice = voice


class MessageConstructor(ABC):
    async def init(self):
        ...


class TextMessageConstructor(
    TextMarkupConstructor,
    KeyboardMarkupConstructor,
    MessageConstructor,
):
    def __init__(self, state: State | None = None):
        self.state = state
        KeyboardMarkupConstructor.__init__(self)
        TextMarkupConstructor.__init__(self)

    def merge(self, constructor: Self, only_emoji_text=False):
        self.add_texts_rows(*constructor.text_map)
        for buttons_row in constructor.keyboard_map:
            self.add_buttons_in_new_row(*buttons_row, only_emoji_text=only_emoji_text)


class PhotoMessageConstructor(
    TextMessageConstructor,
    PhotoMarkupConstructor,
    MessageConstructor,

):
    def __init__(self, state: State | None = None):
        self.state = state
        PhotoMarkupConstructor.__init__(self)
        TextMessageConstructor.__init__(self)

    @property
    def text(self):
        text = super().text
        if text != Emoji.BAN:
            return text


class VoiceMessageConstructor(
    TextMessageConstructor,
    VoiceMarkupConstructor,
    MessageConstructor,
):
    def __init__(self, state: State | None = None):
        self.state = state
        TextMarkupConstructor.__init__(self)
        VoiceMarkupConstructor.__init__(self)

    @property
    def text(self):
        text = super().text
        if text != Emoji.BAN:
            return text
