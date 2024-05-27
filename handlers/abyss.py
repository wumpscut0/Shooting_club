from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.bot_control import BotControl
from markups.core.core_text_messages import Info, Input
from tools.emoji import Emoji

abyss_router = Router()


@abyss_router.callback_query()
async def callback_abyss(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.update_text_message(
        Info, f"Sorry. This button no working so far. {Emoji.CRYING_CAT}"
    )


@abyss_router.message(~StateFilter(None))
async def wrong_type_message_abyss(
    message: Message, bot_control: BotControl, state: FSMContext
):
    await message.delete()

    state_name = await state.get_state()
    guess = ""
    if "text" in state_name:
        guess = "text"
    elif "photo" in state_name:
        guess = "photo"

    if guess is not None:
        guess = f"Try to send {guess}"
    await bot_control.update_text_message(
        Input, f"Wrong message type {Emoji.BROKEN_HEARTH} {guess}", state=state_name)


@abyss_router.message()
async def message_abyss(message: Message, bot_control: BotControl):
    await message.delete()
    await bot_control.create_text_message(
        Info, f"Your message was eaten by the abyss {Emoji.ABYSS}"
    )
