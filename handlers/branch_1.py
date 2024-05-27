import os

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, FSInputFile

from bot.FSM import States
from bot.bot_control import BotControl
from database.__init__ import UserGun
from markups.core.core_text_messages import Input, Conform
from markups.core.core_voice_messages import Voice
from markups.text_messages import ChooseGunForHit, ChooseGunForHitCallbackData, Zones, ZoneCallbackData, Zone, \
    ZoneValueCallbackData, TitleScreen
from tools import Emoji

branch_1 = Router()


@branch_1.callback_query(F.data == "title_screen")
async def title_screen(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.set_context(TitleScreen, bot_control.user_id, auto_return=True)


@branch_1.callback_query(F.data == "guns_list")
async def update_data(callback: CallbackQuery, bot_control: BotControl):
    bot_control.storage.clear()
    await bot_control.set_context(ChooseGunForHit, auto_return=True)


@branch_1.callback_query(F.data == "reset")
async def reset_zones(callback: CallbackQuery, bot_control: BotControl):
    bot_control.storage.clear()
    await bot_control.set_context(Zones, bot_control.user_id, auto_return=True, back_callback_data="guns_list")


@branch_1.callback_query(ChooseGunForHitCallbackData.filter())
async def bullets_select(callback: CallbackQuery, callback_data: ChooseGunForHitCallbackData, bot_control: BotControl):
    bot_control.storage.clear()
    bot_control.storage.gun_id = callback_data.id
    await bot_control.update_text_message(Input, text=f"{Emoji.BULLET} Сколько гильз?", state=States.input_text_bullets)


@branch_1.message(StateFilter(States.input_text_bullets), F.text)
async def input_text_bullets(message: Message, bot_control: BotControl):
    bullets = message.text
    await message.delete()
    try:
        bullets = int(bullets)
    except ValueError:
        await bot_control.update_text_message(Input,
                                              text=f"Вводите только цифры {Emoji.CRYING_CAT}",
                                              state=States.input_text_bullets
                                              )
        return

    if bullets > 1400:
        await bot_control.update_text_message(Input,
                                              text=f"Не более двух цинков за раз {Emoji.CRYING_CAT}",
                                              state=States.input_text_bullets
                                              )
        return

    if bullets < 1:
        await bot_control.update_text_message(Input,
                                              text=f"{Emoji.CLOWN}",
                                              state=States.input_text_bullets
                                              )
        return
    bot_control.storage.bullets = bullets
    await bot_control.set_context(Zones, bot_control.user_id, auto_return=True, back_callback_data="guns_list")


@branch_1.callback_query(ZoneCallbackData.filter())
async def zone(callback: CallbackQuery, callback_data: ZoneCallbackData, bot_control: BotControl):
    await bot_control.update_text_message(Zone,
                                          callback_data.zone, callback_data.max_possibles, callback_data.page
                                          )


@branch_1.callback_query(ZoneValueCallbackData.filter())
async def update_zone_value(callback: CallbackQuery, callback_data: ZoneValueCallbackData, bot_control: BotControl):
    bot_control.storage.update_zone(callback_data.zone, callback_data.value)
    await bot_control.set_context(Zones, bot_control.user_id, auto_return=True, back_callback_data="guns_list")


@branch_1.callback_query(F.data == "save")
async def conform_save(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.update_text_message(Conform,
                                          text=f"Данные верны {Emoji.RED_QUESTION}\n"
                                               f"За гнилой базар придется ответить {Emoji.KNIFE}",
                                          yes_text=f"{Emoji.OK} Подтвердить",
                                          no_text=f"{Emoji.CYCLE} Изменить данные",
                                          yes_callback_data="merge_data",
                                          )


@branch_1.callback_query(F.data == "merge_data")
async def merge_data(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.set_context(ChooseGunForHit)
    await UserGun.merge_data(bot_control.user_id)
    bot_control.storage.clear()
    await bot_control.update_voice_message(Voice, FSInputFile(os.path.join(os.path.dirname(__file__), "..", "audio", "just_remember.ogg")))
