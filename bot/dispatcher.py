import os

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import CallbackQuery, Message

from bot.middleware import BuildBotControl
from handlers import common_router
from handlers.abyss import abyss_router

from handlers.branch_1 import branch_1
from handlers.branch_3 import branch_3
from handlers.commands import commands_router
from handlers.branch_2 import branch_2


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
    branch_1,
    branch_2,
    branch_3,
    abyss_router,
)
