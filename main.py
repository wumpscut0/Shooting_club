import aiofiles
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from bot.bot_control import BotCommands, BotControl, Scavenger

import asyncio

from bot.dispatcher import dispatcher


from database import create_all

PAGE = "guns.txt"


async def get_data_from_origin():
    async with ClientSession() as session:
        async with session.get("https://a1-tir.ru/arsenal") as response:
            async with aiofiles.open(PAGE, "w", encoding="utf-8") as file:
                data = await response.text()
                await file.write(data)
                return data


async def get_guns_generator():
    # await get_data_from_origin()
    await create_all()
    async with aiofiles.open(PAGE, "r", encoding="utf-8") as file:
        guns = await file.read()
    soup = BeautifulSoup(markup=guns, features="html.parser")
    guns = soup.find_all(name="div", class_="t1093")
    for gun in guns:
        try:
            photo = gun.find_next("div", attrs={"data-field-top-value": "146"}).find_next("div", class_="tn-atom t-bgimg")
            name = gun.find_next("div", attrs={"data-field-top-value": "94"})
            header = name.find_next("div", attrs={"data-field-top-value": "94"})
            description = gun.find_next("div", attrs={"data-field-top-value": "232"})
            yield {
                "photo": photo.attrs["data-original"],
                "name": name.get_text("\n"),
                "header": header.get_text("\n"),
                "description": description.get_text("\n"),
            }
        except AttributeError:
            pass


async def main():
    # await create_all()
    Scavenger.scheduler.start()
    await BotControl.bot.set_my_commands(BotCommands.bot_commands)
    await dispatcher.start_polling(BotControl.bot)


if __name__ == '__main__':
    asyncio.run(main())
