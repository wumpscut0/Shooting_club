import os

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import CallbackQuery, Message

from bot.middleware import BuildBotControl
from handlers import common_router
from handlers.abyss import abyss_router

from handlers.basic import basic_router
from handlers.commands import commands_router
from handlers.person_statistic import person_statistic


class MessagePrivateFilter:
    def __call__(self, message: Message):
        return message.chat.type == "private"


class CallbackPrivateFilter:
    def __call__(self, callback: CallbackQuery):
        return callback.message.chat.type == "private"


dispatcher = Dispatcher(
    storage=RedisStorage(
        Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))
    )
)

dispatcher.update.middleware(BuildBotControl())
dispatcher.message.filter(MessagePrivateFilter())
dispatcher.callback_query.filter(CallbackPrivateFilter())
dispatcher.include_routers(
    common_router,
    commands_router,
    basic_router,
    person_statistic,
    abyss_router,
)
