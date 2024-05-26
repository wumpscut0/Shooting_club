from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError

from bot import BotControl, BotCommands
from bot.FSM import States
from markups import Conform, Input, Info, Temp

from markups.specific import TitleScreen
from database.models import User
from tools.emoji import Emoji

commands_router = Router()


@commands_router.message(BotCommands.start())
async def start(message: Message, bot_control: BotControl):
    await message.delete()

    try:
        await (User.add(bot_control.user_id))
    except IntegrityError:
        pass
    await bot_control.set_context(TitleScreen, bot_control.storage.first_name, auto_return=True)


@commands_router.message(BotCommands.exit())
async def exit_(message: Message, bot_control: BotControl):
    await message.delete()

    await bot_control.update_text_message(Temp(text="Good by!"))


@commands_router.message(BotCommands.report())
async def report(message: Message, bot_control: BotControl):
    await message.delete()

    await bot_control.update_text_message(
        Input(f"Enter your message {Emoji.PENCIL}", state=States.input_text_to_admin)
    )


@commands_router.message(StateFilter(States.input_text_to_admin), F.text)
async def send_message_to_admin_accept_input(message: Message, bot_control: BotControl):
    message_ = message.text
    await message.delete()

    await bot_control.send_message_to_admin(message_)
    await bot_control.update_text_message(
        Info(f"Message sent {Emoji.INCOMING_ENVELOPE}")
    )
