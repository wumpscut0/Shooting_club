import os

from aiogram import Bot
from aiogram.enums import InputMediaType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, FSInputFile, InputMediaPhoto

import bot
from markups import Info, InitializeTextMessageMarkup
from markups.core import TextMessageMarkup, AsyncInitializeTextMessageMarkup
from markups.specific import TitleScreen
from tools.emoji import Emoji
from tools.loggers import errors, info
from utils.redis import ShootingClubStorage, TextMessagesPool


class BotCommands:
    bot_commands = [
        BotCommand(
            command="/start", description=f"Get title screen {Emoji.ZAP}"
        ),
        BotCommand(
            command="/exit", description=f"Close interface {Emoji.ZZZ}"
        ),
        BotCommand(
            command="/report", description=f"Send report {Emoji.BUG + Emoji.SHINE_STAR}"
        ),
    ]

    @classmethod
    def start(cls):
        return Command(cls.bot_commands[0].command.lstrip("/"))

    @classmethod
    def exit(cls):
        return Command(cls.bot_commands[1].command.lstrip("/"))

    @classmethod
    def report(cls):
        return Command(cls.bot_commands[2].command.lstrip("/"))


class TextMessagesControl:

    @property
    def context(self):
        return self.storage.context

    async def set_context(
        self, initializer: type[InitializeTextMessageMarkup], *args, auto_return: bool = False, **kwargs
    ):
        self.storage.context = initializer, args, kwargs
        if auto_return:
            await self.return_to_context()

    async def create_text_message(
        self, text_message_markup: TextMessageMarkup | InitializeTextMessageMarkup
    ):
        if isinstance(
            text_message_markup,
            (InitializeTextMessageMarkup, AsyncInitializeTextMessageMarkup),
        ):
            text_message_markup = text_message_markup.text_message_markup

        if self._state is not None:
            await self._state.set_state(text_message_markup.state)

        try:
            message = await self.bot.send_message(
                chat_id=self._user_id,
                text=text_message_markup.text,
                reply_markup=text_message_markup.keyboard,
            )
            self.storage.add_message_id_to_the_pull(message.message_id)
        except TelegramBadRequest:
            errors.critical("Unsuccessfully creating text message.")

    #  This is central operation with bot.
    #  It magic method wanting only special TextMessageMarkup instance for smart update chat dialog in text message case
    async def update_text_message(
        self,
        text_message_markup: TextMessageMarkup | InitializeTextMessageMarkup,
    ):
        if isinstance(
            text_message_markup,
            (InitializeTextMessageMarkup, AsyncInitializeTextMessageMarkup),
        ):
            text_message_markup = text_message_markup.text_message_markup

        if self.contextualize:
            #  It removes all older message from bot and shift context markup in last message.
            await self._contextualize_chat()

        #  Check on heaving FSMContext exists in self (We can initialize BotControl in everywhere, without FSMContext)
        if self._state is not None:
            await self._state.set_state(text_message_markup.state)

        last_message_id = self.storage.last_message_id
        if last_message_id is None:
            await self.create_text_message(text_message_markup)
            return

        try:
            await self.bot.edit_message_text(
                chat_id=self._user_id,
                message_id=last_message_id,
                text=text_message_markup.text,
                reply_markup=text_message_markup.keyboard,
            )
        except TelegramBadRequest:
            await self.delete_message(last_message_id)
            self.storage.pop_last_message_id_from_the_pull()
            await self.update_text_message(text_message_markup)

    async def return_to_context(self):
        try:
            initializer, args, kwargs = self.storage.context
            if InitializeTextMessageMarkup in initializer.__bases__:
                await self.update_text_message(initializer(*args, **kwargs))
            elif AsyncInitializeTextMessageMarkup in initializer.__bases__:
                await self.update_text_message(
                    await initializer(*args, **kwargs).init()
                )
            else:
                errors.critical(
                    f"Incorrect initializer in context.\n"
                    f"Initializer: {initializer}\n"
                    f"Args: {args}"
                    f"Kwargs: {kwargs}"
                )
                raise ValueError
        except (AttributeError, ValueError, BaseException) as e:
            # If we change code with context in redis, then exist chance work this exception
            errors.error(f"broken contex {e}")
            await self.set_context(TitleScreen, self.storage.first_name)
            await self.update_text_message(
                Info(f"Something happened {Emoji.CRYING_CAT} Sorry")
            )

    async def send_message_to_admin(self, message: str):
        message = f"Reply from {self.storage.first_name}\n" f"{message}"
        try:
            await self.bot.send_message(chat_id=os.getenv("GROUP_ID"), text=message)
        except TelegramBadRequest as e:
            errors.error(f"Failed sending message to admin: {message}\n{e}")

    async def _contextualize_chat(self):
        valuables_messages = []
        for message_id in self.storage.message_ids_pull[:-1]:
            if await self.delete_message(message_id):
                valuables_messages.append(message_id)
        try:
            valuables_messages.append(self.storage.message_ids_pull[-1])
            self.storage.message_ids_pull = valuables_messages
        except IndexError:
            pass

    async def delete_message(self, message_id: int, forced_text=f"{Emoji.FROG}"):
        try:
            await self.bot.delete_message(self._user_id, message_id)
        except TelegramBadRequest:
            try:
                await self.bot.edit_message_text(forced_text, self._user_id, message_id)
                return True
            except TelegramBadRequest:
                pass

    async def api_status_code_processing(self, code: int, *expected_codes: int) -> bool:
        if code in expected_codes:
            return True

        if code == 401:
            info.warning(f"Trying unauthorized access. User: {self.user_id}")
            await self.set_context(TitleScreen, self.storage.first_name)
            await self.update_text_message(
                Info(
                    f"Your session expired {Emoji.CRYING_CAT} Please, sign in again {Emoji.DOOR}"
                )
            )

        elif code == 500:
            errors.critical(f"Internal server error.")
            await self.update_text_message(
                Info(
                    f"Internal server error {Emoji.CRYING_CAT + Emoji.BROKEN_HEARTH} Sorry"
                )
            )
        else:
            errors.critical(f"Unexpected status from API: {code}")
            await self.update_text_message(
                Info(f"Something broken {Emoji.CRYING_CAT + Emoji.BROKEN_HEARTH} Sorry")
            )

        return False


class BotControl(TextMessagesControl):
    bot = Bot(os.getenv("TOKEN"), parse_mode="HTML")

    def __init__(
        self, user_id: str, state: FSMContext | None = None, contextualize: bool = True
    ):
        self._user_id = user_id
        self._state = state
        self.contextualize = contextualize

    self.storage = TextMessagesPool(user_id)

    @property
    def user_id(self):
        return str(self._user_id)
