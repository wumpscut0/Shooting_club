from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot import BotControl

common_router = Router()


@common_router.callback_query(F.data == "return_to_context")
async def return_to_context(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.return_to_context()
