from asyncio import sleep
from typing import Dict

from aiogram.filters.callback_data import CallbackData

from markups import (
    InitializeMarkupInterface,
    Conform, LeftRight,
)
from markups.core import (
    TextWidget,
    ButtonWidget,
    DataTextWidget,
    AsyncInitializeMarkupInterface,
)


from database.models import UserGun, get_gun, get_user_gun, Gun
from tools.emoji import Emoji


class TitleScreen(InitializeMarkupInterface):
    def __init__(self, first_name: str):
        super().__init__()
        text_map = [
            DataTextWidget(text=f"Как стрельба", sep=", ", data=first_name, end="?")
        ]
        keyboard_map = [
            [
                ButtonWidget(text=f"{Emoji.FLOPPY_DISC} Внести данные", callback_data="guns_list")
            ],
            [
                ButtonWidget(text=f"{Emoji.DIAGRAM} Cтатистика", callback_data="person_statistic")
            ],
        ]
        self.text_message_markup.text_map = text_map
        self.text_message_markup.keyboard_map = keyboard_map


class ChooseGunForHitCallbackData(CallbackData, prefix="gun"):
    id: int


class ChooseGunForHit(AsyncInitializeMarkupInterface):
    def __init__(self, back_callback_data: str | CallbackData = "title_screen"):
        super().__init__()
        self.back_callback_data = back_callback_data

    async def init(self):
        text_map = [TextWidget(text=f"{Emoji.GUN} Выбери ствол")]
        keyboard_map = []
        for gun in await Gun.get_all():
            keyboard_map.append([ButtonWidget(text=gun.name, callback_data=ChooseGunForHitCallbackData(id=gun.id))])
        keyboard_map.append([ButtonWidget(text=f"{Emoji.BACK}", callback_data=self.back_callback_data)])
        self.text_message_markup.text_map = text_map
        self.text_message_markup.keyboard_map = keyboard_map
        return self


class ZoneCallbackData(CallbackData, prefix="zone"):
    page: int = 0
    zone: str
    max_possibles: int


class Zones(AsyncInitializeMarkupInterface):
    zones_emoji = {
        "10": Emoji.TEN,
        "9": Emoji.NINE,
        "8": Emoji.EIGHT,
        "7": Emoji.SEVEN,
        "6": Emoji.SIX,
        "5": Emoji.FIVE
    }

    def __init__(self, _gun_id: int, bullets: int, zones: Dict[str, int], back_callback_data: str | CallbackData = "return_to_context"):
        super().__init__()
        self._gun_id = _gun_id
        self._bullets = bullets
        self._zones = zones
        self.back_callback_data = back_callback_data

    async def init(self):
        text_map = [DataTextWidget(text=f"{Emoji.SMALL_RED_TRIANGLE_DOWN} Оружие", data=(await get_gun(self._gun_id)).name)]
        max_possibles = self._bullets - sum(self._zones.values())
        keyboard_map = []
        row = []
        chunk = 0
        for zone, value in self._zones.items():
            button = ButtonWidget(text=f"{self.zones_emoji[zone]}: {value}", callback_data=ZoneCallbackData(
                zone=zone,
                max_possibles=max_possibles
            ))
            if chunk == 3:
                chunk = 0
                keyboard_map.append(row)
                row = []
            row.append(button)
            chunk += 1

        keyboard_map.append(row)
        miss = self._bullets - sum(self._zones.values())
        text_map.append(DataTextWidget(
            text=f"{Emoji.SYNTH_MUSCLE if not miss else Emoji.GLASS_OF_MILK} Промахов",
            data=str(miss)
        ))
        self.text_message_markup.text_map = text_map
        self.text_message_markup.keyboard_map = keyboard_map
        self.text_message_markup.add_button_in_new_row(
            ButtonWidget(text=f"{Emoji.FLOPPY_DISC} Сохранить", callback_data="save")
        )
        self.text_message_markup.add_button_in_new_row(
            ButtonWidget(text=f"{Emoji.CYCLE} Сбросить", callback_data="reset")
        )
        self.text_message_markup.add_button_in_new_row(
            ButtonWidget(text=f"{Emoji.DENIAL} Отмена", callback_data=self.back_callback_data)
        )
        return self


class ZoneValueCallbackData(CallbackData, prefix="zone_value"):
    zone: str
    value: int


class Zone(InitializeMarkupInterface):
    _buttons_per_page = 20

    def __init__(self, zone: str, max_possibles: int, current_page: int = 0, back_callback_data: str | CallbackData = "return_to_context"):
        super().__init__()
        text_map = [TextWidget(text=Zones.zones_emoji[zone])]
        pages = []
        page = []
        count = 0
        for hit in range(1, max_possibles + 1):
            button = ButtonWidget(text=str(hit), callback_data=ZoneValueCallbackData(zone=zone, value=hit))
            if count == self._buttons_per_page:
                count = 0
                pages.append(page)
                page = []
            page.append(button)
            count += 1
        pages.append(page)

        size_pages = len(pages)
        #
        keyboard_map = []
        row = []
        chunk = 0
        for button in pages[current_page]:
            if chunk == 2:
                chunk = 0
                keyboard_map.append(row)
                row = []
            row.append(button)
            chunk += 1
        keyboard_map.append(row)
        self.text_message_markup.keyboard_map = keyboard_map
        #
        left_right = LeftRight(
            left_callback_data=ZoneCallbackData(page=current_page - 1 % size_pages, zone=zone, max_possibles=max_possibles),
            right_callback_data=ZoneCallbackData(page=current_page + 1 % size_pages, zone=zone, max_possibles=max_possibles)
        )
        back = ButtonWidget(
            text=f"{Emoji.BACK}",
            callback_data=back_callback_data
        )
        self.text_message_markup.text_map = text_map
        if max_possibles > self._buttons_per_page:
            self.text_message_markup.attach(left_right)
        self.text_message_markup.add_button_in_new_row(back)


class GunStatisticCallbackData(CallbackData, prefix="gun_statistic"):
    id: int


class StatisticGunsList(AsyncInitializeMarkupInterface):
    def __init__(self, user_id: str, back_callback_data: str | CallbackData = "title_screen"):
        super().__init__()
        self._user_id = user_id
        self.back_callback_data = back_callback_data

    async def init(self):
        gun = await UserGun.get_most_popularity_gun(str(self._user_id))
        text_map = [DataTextWidget(text=f"{Emoji.FIRE} Любимое оружие", data=gun.name)]
        keyboard_map = []
        data = await UserGun.get_user_guns_by_user(user_id=self._user_id)
        for statistic, gun in data:
            keyboard_map.append([ButtonWidget(text=gun.name, callback_data=GunStatisticCallbackData(id=gun.id))])
        keyboard_map.append([ButtonWidget(text=f"{Emoji.BACK}", callback_data=self.back_callback_data)])

        self.text_message_markup.text_map = text_map
        self.text_message_markup.keyboard_map = keyboard_map
        return self


class GunInfoCallbackData(CallbackData, prefix="gun_info"):
    id: int

class GunStatistic(AsyncInitializeMarkupInterface):
    _worst_point = 5
    _best_point = 10
    _coefficients = {
        "5": 0.5,
        "6": 0.6,
        "7": 0.7,
        "8": 0.8,
        "9": 0.9,
        '10': 1
    }
    _total_areas = len(_coefficients)

    def __init__(self, gun_id: int, user_id, back_callback_data: str | CallbackData = "return_to_context"):
        super().__init__()
        self._user_id = user_id
        self._gun_id = gun_id
        self.back_callback_data = back_callback_data

    async def init(self):
        statistic, gun = await get_user_gun(gun_id=self._gun_id, user_id=self._user_id)
        print(statistic.zones)
        print(statistic.bullets_fired)
        weighted_hits = sum(statistic.zones[zone] * self._coefficients[zone] for zone in statistic.zones)
        precision = round(weighted_hits / statistic.bullets_fired * 100, 2)
        text_map = [
            TextWidget(text=f"{Emoji.GUN} {gun.name}"),
            DataTextWidget(text=f"{Emoji.SIGHT} Точность", data=precision, end="%"),
            DataTextWidget(text=f"{Emoji.BULLET} Пуль выпущено", data=statistic.bullets_fired)
        ]
        keyboard_map = [
            [
                ButtonWidget(text=f"{Emoji.INFO} Информация", callback_data=GunInfoCallbackData(id=self._gun_id)),
            ],
            [
                ButtonWidget(text=f"{Emoji.BACK}", callback_data=self.back_callback_data),
            ],
        ]

        self.text_message_markup.text_map = text_map
        self.text_message_markup.keyboard_map = keyboard_map
        return self
