from datetime import datetime, timedelta

from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from bot import BotControl
from tools.loggers import errors


class Scavenger:
    scheduler = AsyncIOScheduler()
    scheduler.configure(jobstore={"default": RedisJobStore()}, job_defaults={"coalesce": False})

    @classmethod
    async def add_target(cls, chat_id: int, message_id: int, await_time: int):
        """
        :param message_id: message for delete
        :param chat_id: telegram chat
        :param await_time: minutes
        :return:
        """
        cls.scheduler.add_job(
            cls.delete_message,
            args=(chat_id, message_id, await_time),
            trigger="date",
            next_run_time=datetime.now() + timedelta(minutes=await_time)
        )

    @classmethod
    async def delete_message(cls, chat_id: int, message_id: int, await_time: int | None = None):
        try:
            await BotControl.bot.delete_message(
                chat_id,
                message_id
            )
        except TelegramBadRequest:
            errors.exception(f"Failed delete message {message_id} for chat {chat_id}\n"
                             f"Scavenger commentary: сука, я зря ждал {await_time} минут?\n")
