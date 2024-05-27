from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.bot_control import BotControl
from database import Gun
from markups.core.core_photo_messages import Photo
from markups.text_messages import GunStatisticCallbackData, GunStatistic, GunInfoCallbackData, PersonGunsList

branch_2 = Router()


@branch_2.callback_query(F.data == "person_gun_list")
async def person_statistic_(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.set_context(PersonGunsList, bot_control.user_id, auto_return=True)


@branch_2.callback_query(GunStatisticCallbackData.filter())
async def gun_statistic_person(callback: CallbackQuery, callback_data: GunStatisticCallbackData,
                               bot_control: BotControl):
    await bot_control.update_text_message(
        GunStatistic,
        bot_control.user_id, callback_data.id
    )


@branch_2.callback_query(GunInfoCallbackData.filter())
async def gun_info(callback: CallbackQuery, callback_data: GunInfoCallbackData, bot_control: BotControl):
    gun = await Gun.get_gun(callback_data.id)
    await bot_control.update_photo_message(Photo, gun.photo,
                                           f'{gun.name}\n{gun.header}\n{gun.description}',
                                           GunStatisticCallbackData(id=callback_data.id
                                                                    ))
