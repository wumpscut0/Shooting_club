from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.bot_control import BotControl
from database import Gun
from markups.core.core_photo_messages import Photo
from markups.text_messages import GunStatisticCallbackData, GunStatistic, GunInfoCallbackData, PersonGunsList, \
    GunsGlobalListCallbackData, GunsGlobalList, GlobalGun

branch_3 = Router()


@branch_3.callback_query(F.data == "global_statistic")
async def global_guns_list(
        callback: CallbackQuery,
        bot_control: BotControl
):
    await bot_control.set_context(GunsGlobalList, auto_return=True)


@branch_3.callback_query(GunsGlobalListCallbackData.filter())
async def global_gun(
        callback: CallbackQuery,
        callback_data: GunsGlobalListCallbackData,
        bot_control: BotControl
):
    await bot_control.update_text_message(GlobalGun, callback_data.id)
