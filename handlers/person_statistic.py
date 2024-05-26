from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, callback_data
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton

from bot import BotControl
from bot.FSM import States
from database.models import UserGun, get_gun
from markups import Input, Conform, Info
from aiogram.utils.keyboard import InlineKeyboardMarkup
from markups.core import PhotoMessageMarkup, ButtonWidget
from markups.specific import ChooseGunForHit, ChooseGunForHitCallbackData, Zones, ZoneCallbackData, Zone, \
    ZoneValueCallbackData, TitleScreen, StatisticGunsList, GunStatisticCallbackData, GunStatistic, GunInfoCallbackData
from tools import Emoji

person_statistic = Router()


@person_statistic.callback_query(F.data == "person_statistic")
async def person_statistic_(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.set_context(StatisticGunsList, bot_control.user_id, auto_return=True)


@person_statistic.callback_query(GunStatisticCallbackData.filter())
async def gun_statistic_person(callback: CallbackQuery, callback_data: GunStatisticCallbackData,
                               bot_control: BotControl):
    await bot_control.update_text_message(await GunStatistic(callback_data.id, bot_control.user_id).init())


@person_statistic.callback_query(GunInfoCallbackData.filter())
async def gun_info(callback: CallbackQuery, callback_data: GunInfoCallbackData, bot_control: BotControl):
    bot_control.storage.gun_id = callback_data.id
    gun = await get_gun(callback_data.id)
    await bot_control.delete_message(bot_control.storage.last_message_id)
    message = await bot_control.bot.send_photo(
        photo=gun.photo,
        chat_id=bot_control.user_id,
        caption=f'{gun.name}\n{gun.header}\n{gun.description}',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=f"{Emoji.DENIAL} Закрыть", callback_data="close_photo")]]),
    )

    bot_control.storage.photo_message_id = message.message_id


@person_statistic.callback_query(F.data == "close_photo")
async def close_photo(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.delete_message(bot_control.storage.photo_message_id)
    await bot_control.update_text_message(await GunStatistic(bot_control.storage.gun_id, bot_control.user_id).init())
