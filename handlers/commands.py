from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError


from bot.FSM import States
from bot.bot_control import BotCommands, BotControl
from markups.core.core_text_messages import Input, Info

from database.__init__ import User
from tools.emoji import Emoji

commands_router = Router()


@commands_router.message(BotCommands.start())
async def continue_(message: Message, bot_control: BotControl):
    await message.delete()
    try:
        await (User.add(bot_control.user_id))
    except IntegrityError:
        pass
    await bot_control.return_to_context()


@commands_router.message(BotCommands.exit())
async def exit_(message: Message, bot_control: BotControl):
    await message.delete()

    await bot_control.delete_message(bot_control._messages_pool.last_message_id_from_the_chat)


@commands_router.message(BotCommands.report())
async def report(message: Message, bot_control: BotControl):
    await message.delete()

    await bot_control.update_text_message(
        Input, f"О чем вы бы хотели сказать? {Emoji.PENCIL}", state=States.input_text_to_admin
    )


@commands_router.message(StateFilter(States.input_text_to_admin), F.text)
async def send_message_to_admin_accept_input(message: Message, bot_control: BotControl):
    message_ = message.text
    await message.delete()

    await bot_control.send_message_to_admin(message_)
    await bot_control.update_text_message(
        Info, f"Сообщение отправлено {Emoji.INCOMING_ENVELOPE} Спасибо"
    )
