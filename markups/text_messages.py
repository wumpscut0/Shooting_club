import random

from aiogram.filters.callback_data import CallbackData

from markups.core import (
    TextWidget,
    ButtonWidget,
    DataTextWidget, TextMessageConstructor
)

from database import UserGun, Gun
from markups.core.core_keyboards import LeftRight
from tools import split
from tools.emoji import Emoji
from utils.redis import UserStorage, ShootingClubStorage

phrases = [
    "Мы их сомнем",
    "Настал наш день",
    "Они прямо у нас под носом",
    "Киров на связи",
    "Сначала предупредительный",
    "Армагеддон на пороге",
]


class TitleScreen(TextMessageConstructor):
    def __init__(self, user_id: str):
        super().__init__()
        storage = UserStorage(user_id)
        self._text_map = [
            TextWidget(text=random.choice(phrases))
        ]
        self._keyboard_map = [
            [
                ButtonWidget(text=f"{Emoji.FLOPPY_DISC} Внести данные", callback_data="guns_list")
            ],
            [
                ButtonWidget(text=f"{Emoji.DIAGRAM} Личная статистика", callback_data="person_gun_list")
            ],
            [
                ButtonWidget(text=f"{Emoji.DIAGRAM_TOP} Общая статистика", callback_data="global_statistic")
            ]
        ]

    async def init(self):
        self.text_map = self._text_map
        self.keyboard_map = self._keyboard_map
         

class ChooseGunForHitCallbackData(CallbackData, prefix="gun"):
    id: int


class ChooseGunForHit(TextMessageConstructor):
    def __init__(self, back_callback_data: str | CallbackData = "title_screen"):
        super().__init__()
        self.info = TextWidget(text=f"{Emoji.GUN} Выбери пушку")
        self.back = ButtonWidget(text=f"{Emoji.BACK}", callback_data=back_callback_data)

    async def init(self):
        keyboard_map = []
        for gun in await Gun.get_all():
            keyboard_map.append([ButtonWidget(text=gun.name, callback_data=ChooseGunForHitCallbackData(id=gun.id))])
        self.add_texts_rows(self.info)
        self.keyboard_map = keyboard_map
        self.add_buttons_in_new_row(self.back)


class ZoneCallbackData(CallbackData, prefix="zone"):
    page: int = 0
    zone: str
    max_possibles: int


class Zones(TextMessageConstructor):
    zones_emoji = {
        "10": Emoji.TEN,
        "9": Emoji.NINE,
        "8": Emoji.EIGHT,
        "7": Emoji.SEVEN,
        "6": Emoji.SIX,
        "5": Emoji.FIVE
    }

    def __init__(self, user_id: str, back_callback_data: str | CallbackData = "return_to_context"):
        super().__init__()
        self._storage = ShootingClubStorage(user_id)
        self._back = ButtonWidget(text=f"{Emoji.DENIAL} Отмена", callback_data=back_callback_data)

    async def init(self):
        zones = self._storage.zones
        text_map = [
            DataTextWidget(
                text=f"{Emoji.SMALL_RED_TRIANGLE_DOWN} Оружие",
                data=(await Gun.get_gun(self._storage.gun_id)).name
            )
        ]
        max_possibles = self._storage.bullets - sum(zones.values())
        miss = self._storage.bullets - sum(zones.values())
        text_map.append(DataTextWidget(
            text=f"{Emoji.SYNTH_MUSCLE if not miss else Emoji.GLASS_OF_MILK} Промахов",
            data=str(miss)
        ))
        save_button = ButtonWidget(text=f"{Emoji.FLOPPY_DISC} Сохранить", callback_data="save")
        reset_button = ButtonWidget(text=f"{Emoji.CYCLE} Сбросить", callback_data="reset")
        zones_buttons = [
            ButtonWidget(text=f"{self.zones_emoji[zone]}: {value}", callback_data=ZoneCallbackData(
                zone=zone,
                max_possibles=max_possibles
            ))
            for zone, value in zones.items()
        ]

        self.text_map = text_map
        self.keyboard_map = split(3, zones_buttons)
        self.add_buttons_as_column(
            save_button,
            reset_button,
            self._back
        )
         

class ZoneValueCallbackData(CallbackData, prefix="zone_value"):
    zone: str
    value: int


class Zone(TextMessageConstructor):
    _buttons_per_page = 20

    def __init__(
            self,
            zone: str,
            max_possibles: int,
            current_page: int = 0,
            back_callback_data: str | CallbackData = "return_to_context"
    ):
        super().__init__()
        self._max_possibles = max_possibles
        self._zone_text = TextWidget(text=Zones.zones_emoji[zone])
        hits_buttons = [
            ButtonWidget(text=str(hit), callback_data=ZoneValueCallbackData(zone=zone, value=hit))
            for hit in range(1, max_possibles + 1)
        ]
        paginated_hits_buttons = split(self._buttons_per_page, hits_buttons)
        total_pages = len(paginated_hits_buttons)
        self._hits_buttons = split(2, paginated_hits_buttons[current_page])
        self._left_right_buttons = LeftRight(
            left_callback_data=ZoneCallbackData(
                page=current_page - 1 % total_pages,
                zone=zone,
                max_possibles=max_possibles
            ),
            right_callback_data=ZoneCallbackData(
                page=current_page + 1 % total_pages,
                zone=zone,
                max_possibles=max_possibles
            )
        )
        self._back_button = ButtonWidget(
            text=f"{Emoji.BACK}",
            callback_data=back_callback_data
        )

    async def init(self):
        self.add_texts_rows(self._zone_text)
        self.keyboard_map = self._hits_buttons
        if self._max_possibles > self._buttons_per_page:
            self.add_buttons_in_new_row(*self._left_right_buttons.keyboard_map)
        self.add_button_in_new_row(self._back_button)


class GunStatisticCallbackData(CallbackData, prefix="gun_statistic"):
    id: int


class PersonGunsList(TextMessageConstructor):
    def __init__(self, user_id: str, back_callback_data: str | CallbackData = "title_screen"):
        super().__init__()
        self._user_id = user_id
        self._back_button = ButtonWidget(text=f"{Emoji.BACK}", callback_data=back_callback_data)

    async def init(self):
        favorite_gun = await UserGun.get_most_popularity_gun(self._user_id)
        favorite_gun_text = DataTextWidget(text=f"{Emoji.WHITE_BLACK_START} Любимое оружие", data=favorite_gun.name)

        data = await UserGun.get_user_guns_by_user(user_id=self._user_id)

        guns_buttons = []
        for statistic, gun in data:
            gun_button = ButtonWidget(text=gun.name, callback_data=GunStatisticCallbackData(id=gun.id))
            if gun.name == favorite_gun.name:
                gun_button.mark = Emoji.WHITE_BLACK_START
            guns_buttons.append(gun_button)
        guns_buttons.append(self._back_button)

        self.add_texts_rows(favorite_gun_text)
        self.add_buttons_as_column(*guns_buttons)


class GunInfoCallbackData(CallbackData, prefix="gun_info"):
    id: int


class GunStatistic(TextMessageConstructor):
    _coefficients = {
        "5": 0.5,
        "6": 0.6,
        "7": 0.7,
        "8": 0.8,
        "9": 0.9,
        '10': 1
    }
    _total_areas = len(_coefficients)

    def __init__(self, user_id, gun_id: int, back_callback_data: str | CallbackData = "person_gun_list"):
        super().__init__()
        self._user_id = user_id
        self._gun_id = gun_id
        self._info_gun_button = ButtonWidget(
            text=f"{Emoji.INFO} Информация",
            callback_data=GunInfoCallbackData(id=gun_id)
        )
        self._back_button = ButtonWidget(text=f"{Emoji.BACK}", callback_data=back_callback_data)

    async def init(self):
        statistic, gun = await UserGun.get_user_statistic_by_gun_and_id(gun_id=self._gun_id, user_id=self._user_id)

        text_map = [
            TextWidget(text=f"{Emoji.GUN} {gun.name}"),
            DataTextWidget(text=f"{Emoji.SIGHT} Точность", data=str(statistic.precision()), end="%"),
            DataTextWidget(text=f"{Emoji.BULLET} Пуль выпущено", data=str(statistic.bullets_fired))
        ]
        keyboard_map = [
            [
                self._info_gun_button,
            ],
            [
                self._back_button
            ],
        ]

        self.text_map = text_map
        self.keyboard_map = keyboard_map


class GunsGlobalListCallbackData(CallbackData, prefix="global_guns_list"):
    id: int


class GunsGlobalList(TextMessageConstructor):
    def __init__(self):
        super().__init__()

    async def init(self):
        text = TextWidget(text=Emoji.GUN)
        guns_data = set(
            (gun.name, gun.id)
            for statistic, gun in await UserGun.get_users_statistic()
        )
        buttons = [
            ButtonWidget(text=name, callback_data=GunsGlobalListCallbackData(id=id_))
            for name, id_ in guns_data
        ] + [
            ButtonWidget(text=Emoji.BACK, callback_data="title_screen")
        ]
        self.add_texts_rows(text)
        self.add_buttons_as_column(*buttons)


class GlobalGun(TextMessageConstructor):
    _numbers = (
        Emoji.CROWN,
        Emoji.SYNTH_MUSCLE,
        Emoji.MUSCLE,
        Emoji.MONKEY
    )

    def __init__(self, gun_id: int):
        super().__init__()
        self._gun_id = gun_id

    async def init(self):
        leaders_list = sorted(await UserGun.get_users_statistic_by_gun_id(self._gun_id), key=lambda item: item.precision(), reverse=True)
        text_widgets = [TextWidget(text=Emoji.GUN + " " + (await Gun.get_gun(self._gun_id)).name)]
        for i, statistic in enumerate(leaders_list):
            name = UserStorage(statistic.user_id).name
            text_widgets.append(
                DataTextWidget(
                    text=f"{self._numbers[i]}  {"Unknown user" if name is None else name}",
                    data=f" . ݁₊ ⊹ . ݁˖ . ݁{Emoji.BULLET} {statistic.bullets_fired} {Emoji.SIGHT} {statistic.precision()}%\n"
                )
            )
        self.add_texts_rows(*text_widgets)
        self.add_button_in_new_row(ButtonWidget(text=Emoji.BACK, callback_data="return_to_context"))