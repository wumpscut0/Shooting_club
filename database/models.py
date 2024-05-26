from typing import List, Tuple

from pydantic import BaseModel
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey, JSON, update
)
from sqlalchemy.orm import DeclarativeBase, relationship, class_mapper
from sqlalchemy import select, insert, and_, func
from sqlalchemy.orm import selectinload

from typing import Dict


import os


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv, find_dotenv

from tools.loggers import info
from utils.redis import UserStorage

load_dotenv(find_dotenv())
print(os.getenv("DATABASE") + "/shooting_club")
engine = create_async_engine(os.getenv("DATABASE") + "/shooting_club")
Session = async_sessionmaker(engine, expire_on_commit=False)


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class Base(DeclarativeBase):
    ...


class GunModel(BaseModel):
    id: int
    photo: str
    name: str
    header: str
    description: str


class UserGunModel(BaseModel):
    user_id: str
    gun_id: int
    bullets_fired: int
    zones: dict


class UserGun(Base):
    __tablename__ = "user_gun"
    user_id = Column(ForeignKey("user.id"), primary_key=True)
    gun_id = Column(ForeignKey("gun.id"), primary_key=True)
    bullets_fired = Column(Integer, default=0)
    zones = Column(JSON, default={"5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0})

    gun = relationship("Gun")
    user = relationship("User")

    def as_model(self) -> UserGunModel:
        data = {}
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)
        return UserGunModel.model_validate(data)

    @staticmethod
    async def get_most_popularity_gun(user_id: str):
        _coefficients = {
            "5": 0.5,
            "6": 0.6,
            "7": 0.7,
            "8": 0.8,
            "9": 0.9,
            '10': 1
        }
        async with Session.begin() as session:
            gun_ids = (await session.execute(select(
                UserGun.gun_id, func.max(UserGun.bullets_fired)
            ).where(UserGun.user_id == user_id).group_by(UserGun.gun_id))).scalars()
            precisions = []
            for gun_id in gun_ids:
                statistic, gun = await get_user_gun(gun_id=gun_id, user_id=user_id)
                weighted_hits = sum(statistic.zones[zone] * _coefficients[zone] for zone in statistic.zones)
                precision = round(weighted_hits / statistic.bullets_fired * 100, 2)
                precisions.append((gun_id, precision))
            gun_id, _ = max(precisions, key=lambda elem: elem[1])

        return await get_gun(gun_id)

    @staticmethod
    async def get_user_guns_by_user(user_id: str) -> List[Tuple[UserGunModel, GunModel]]:
        async with Session.begin() as session:
            return [
                (user_gun.as_model(), user_gun.gun.as_model())
                for user_gun in
                (await session.execute(select(UserGun).where(UserGun.user_id == str(user_id)).options(selectinload(UserGun.gun)))).scalars()
            ]

    @staticmethod
    async def merge_data(user_id: str):
        storage = UserStorage(user_id)
        gun_id = storage.gun_id
        info.info(f"User {user_id} merge data {storage.zones}")
        async with Session.begin() as session:
            user_gun = (await session.execute(
                select(UserGun).filter(
                    and_(UserGun.user_id == str(user_id), UserGun.gun_id == gun_id)))).scalar_one_or_none()
            if user_gun is None:
                new_user_gun = UserGun(user_id=user_id, gun_id=gun_id)
                session.add(new_user_gun)
                await session.flush()
                user_gun = new_user_gun
            total_zones = user_gun.zones
            data_for_merge = {}
            print(f"merge {total_zones.values()} with {storage.zones.values()}")
            for i, value in enumerate(map(sum, zip(total_zones.values(), storage.zones.values())), start=5):
                data_for_merge[str(i)] = value
            print(f"merge bullets {user_gun.bullets_fired} with {storage.bullets}")
            await session.execute(
                update(UserGun).values(
                    {"bullets_fired": UserGun.bullets_fired + storage.bullets, "zones": data_for_merge}).filter(
                    and_(UserGun.gun_id == gun_id, UserGun.user_id == user_id)))
            storage.clear()


class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)

    def as_model(self):
        data = {}
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)
        return data

    @classmethod
    async def add(cls, user_id: str):
        async with Session.begin() as session:
            await session.execute(insert(User).values({"id": user_id}))


class Gun(Base):
    __tablename__ = "gun"
    id = Column(
        Integer, primary_key=True
    )
    photo = Column(String)
    name = Column(
        String
    )
    header = Column(
        String
    )
    description = Column(
        String
    )

    def as_model(self):
        data = {}
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)
        return GunModel.model_validate(data)

    @classmethod
    async def get_all(cls):
        async with Session.begin() as session:
            return [
                gun.as_model()
                for gun in
                (await session.execute(select(Gun))).scalars()
            ]

    @classmethod
    async def insert_gun(cls, data: Dict):
        async with Session.begin() as session:
            await session.execute(insert(Gun).values(**data))


async def get_users_statistic() -> list[UserGunModel]:
    async with Session.begin() as session:
        return [
            gun.as_model()
            for gun in (await session.execute(select(UserGun))).scalars()
        ]


async def get_gun(gun_id: int) -> GunModel:
    async with Session.begin() as session:
        return (await session.get(Gun, gun_id)).as_model()


async def get_user_gun(gun_id: int, user_id: str):
    async with Session.begin() as session:
        user_gun = (await session.execute(select(UserGun).filter(and_(UserGun.user_id == user_id, UserGun.gun_id == gun_id)).options(selectinload(UserGun.gun)))).scalar()
        gun = user_gun.gun.as_model()
        return user_gun, gun


