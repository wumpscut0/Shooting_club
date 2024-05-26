from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, InputFile

from bot import BotControl
from bot.FSM import States
from database.models import UserGun
from markups import Input, Conform, Info
from markups.specific import ChooseGunForHit, ChooseGunForHitCallbackData, Zones, ZoneCallbackData, Zone, \
    ZoneValueCallbackData, TitleScreen
from tools import Emoji

basic_router = Router()

# leaders_table


@basic_router.callback_query(F.data == "title_screen")
async def title_screen(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.set_context(TitleScreen, bot_control.storage.first_name, auto_return=True)


@basic_router.callback_query(F.data == "guns_list")
async def update_data(callback: CallbackQuery, bot_control: BotControl):
    bot_control.storage.clear()
    await bot_control.set_context(ChooseGunForHit, auto_return=True)


@basic_router.callback_query(F.data == "reset")
async def reset_zones(callback: CallbackQuery, bot_control: BotControl):
    bot_control.storage.clear()
    await bot_control.set_context(Zones, bot_control.storage.gun_id, bot_control.storage.bullets, bot_control.storage.zones, auto_return=True, back_callback_data="guns_list")


@basic_router.callback_query(ChooseGunForHitCallbackData.filter())
async def zones(callback: CallbackQuery, callback_data: ChooseGunForHitCallbackData, bot_control: BotControl):
    bot_control.storage.gun_id = callback_data.id
    bot_control.storage.clear()
    await bot_control.update_text_message(Input(text=f"{Emoji.BULLET} Сколько гильз?", state=States.input_text_bullets))


@basic_router.message(StateFilter(States.input_text_bullets), F.text)
async def input_text_bullets(message: Message, bot_control: BotControl):
    bullets = message.text
    await message.delete()
    try:
        bullets = int(bullets)
    except ValueError:
        await bot_control.update_text_message(Input(
            text=f"Вводите только цифры {Emoji.CRYING_CAT}",
            state=States.input_text_bullets
        ))
        return

    if bullets > 1400:
        await bot_control.update_text_message(Input(
            text=f"Не более двух цинков за раз {Emoji.CRYING_CAT}",
            state=States.input_text_bullets
        ))
        return

    if bullets < 1:
        await bot_control.update_text_message(Input(
            text=f"{Emoji.CLOWN}",
            state=States.input_text_bullets
        ))
        return
    bot_control.storage.bullets = bullets
    await bot_control.set_context(Zones, bot_control.storage.gun_id, bullets, bot_control.storage.zones, auto_return=True, back_callback_data="guns_list")


@basic_router.callback_query(ZoneCallbackData.filter())
async def zone(callback: CallbackQuery, callback_data: ZoneCallbackData, bot_control: BotControl):
    await bot_control.update_text_message(Zone(callback_data.zone, callback_data.max_possibles, callback_data.page))


@basic_router.callback_query(ZoneValueCallbackData.filter())
async def update_zone_value(callback: CallbackQuery, callback_data: ZoneValueCallbackData, bot_control: BotControl):
    bot_control.storage.update_zone(callback_data.zone, callback_data.value)
    await bot_control.set_context(Zones, bot_control.storage.gun_id, bot_control.storage.bullets, bot_control.storage.zones, auto_return=True, back_callback_data="guns_list")


@basic_router.callback_query(F.data == "save")
async def conform_save(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.update_text_message(Conform(
        text=f"Данные верны {Emoji.RED_QUESTION}\n"
             f"За гнилой базар придется ответить {Emoji.KNIFE}",
        yes_text=f"{Emoji.OK} Подтвердить",
        no_text=f"{Emoji.CYCLE} Изменить данные",
        yes_callback_data="merge_data",
    ))


@basic_router.callback_query(F.data == "merge_data")
async def merge_data(callback: CallbackQuery, bot_control: BotControl):
    await bot_control.set_context(ChooseGunForHit)
    await UserGun.merge_data(bot_control.user_id)
    bot_control.storage.clear()
    await bot_control.update_text_message(Info(f"Данные сохранены {Emoji.TICK}"))
    message = await bot_control.bot.send_voice(bot_control.user_id, InputFile("just_remember.mp3"))

