import pickle
from typing import Union, Any, Dict, Tuple

from redis import Redis
from redis.commands.core import ResponseT
from redis.typing import KeyT, ExpiryT, AbsExpiryT

from markups.core import TextMessageConstructor
from tools.loggers import errors


class CustomRedis(Redis):
    def set(
        self,
        name: KeyT,
        value: Any,
        ex: Union[ExpiryT, None] = None,
        px: Union[ExpiryT, None] = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: Union[AbsExpiryT, None] = None,
        pxat: Union[AbsExpiryT, None] = None,
    ) -> ResponseT:
        return super().set(
            name,
            pickle.dumps(value),
            ex,
            px,
            nx,
            xx,
            keepttl,
            get,
            exat,
            pxat,
        )

    def get(self, name: KeyT) -> ResponseT:
        result = super().get(name)
        if result is not None:
            return pickle.loads(result)

    def setex(self, name: KeyT, time: ExpiryT, value: Any) -> ResponseT:
        return super().setex(
            name,
            time,
            pickle.dumps(value),
        )

    def getex(
        self,
        name: KeyT,
        ex: Union[ExpiryT, None] = None,
        px: Union[ExpiryT, None] = None,
        exat: Union[AbsExpiryT, None] = None,
        pxat: Union[AbsExpiryT, None] = None,
        persist: bool = False,
    ) -> ResponseT:
        result = super().getex(name, ex, px, exat, pxat, persist)
        if result is not None:
            return pickle.loads(result)


class RedisSetUp:
    _storage = CustomRedis(
        host="localhost", port=6379, db=1
    )

    def __init__(self, user_id: str):
        self._user_id = user_id


class UserStorage(RedisSetUp):
    @property
    def name(self):
        return self._storage.get(f"name:{self._user_id}")

    @name.setter
    def name(self, data: Any):
        self._storage.set(f"name:{self._user_id}", data)


class MessagesPool(RedisSetUp):

    @property
    def chat_messages_ids_pull(self):
        pull = self._storage.get(f"chat_messages_ids_pull:{self._user_id}")
        if pull is None:
            return []
        return pull

    @property
    def last_message_id_from_the_chat(self):
        try:
            return self.chat_messages_ids_pull[-1]
        except IndexError:
            pass

    def add_message_id_to_the_chat_pull(self, message_id: int):
        pull = self.chat_messages_ids_pull
        pull.append(message_id)
        self.chat_messages_ids_pull = pull

    def pop_last_message_id_from_the_chat_pull(self):
        pull = self.chat_messages_ids_pull
        try:
            pull.pop()
            self.chat_messages_ids_pull = pull
        except IndexError:
            pass

    def remove_message_id_form_the_chat_pull(self, message_id: int):
        pull = self.chat_messages_ids_pull
        try:
            pull.remove(message_id)
            self.chat_messages_ids_pull = pull
        except ValueError:
            pass

    @chat_messages_ids_pull.setter
    def chat_messages_ids_pull(self, data: Any):
        self._storage.set(f"chat_messages_ids_pull:{self._user_id}", data)


class ShootingClubStorage(RedisSetUp):
    @property
    def context(self):
        return self._storage.get(f"context:{self._user_id}")

    @context.setter
    def context(self, context: Tuple[TextMessageConstructor, Tuple[Any, ...], Dict[str, Any]]):
        self._storage.set(f"context:{self._user_id}", context)

    @property
    def bullets(self):
        return self._storage.get(f"bullets:{self._user_id}")

    @bullets.setter
    def bullets(self, quantity: int):
        self._storage.set(f"bullets:{self._user_id}", quantity)

    @property
    def zones(self) -> Dict:
        value = self._storage.get(f"zones:{self._user_id}")
        return value

    def update_zone(self, zone: str, value: int):
        zones = self.zones
        if zones is None:
            zones = {"5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0}
        zones.update({zone: value})
        self._storage.set(f"zones:{self._user_id}", zones)

    def clear(self):
        self._storage.set(f"zones:{self._user_id}", {"5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0})

    @property
    def milk(self):
        if self.zones is None:
            return self.bullets
        else:
            return self.bullets - sum(self.zones.values())

    @property
    def gun_id(self):
        return self._storage.get(f"gun_id:{self._user_id}")

    @gun_id.setter
    def gun_id(self, gun_id: int):
        self._storage.set(f"gun_id:{self._user_id}", gun_id)
