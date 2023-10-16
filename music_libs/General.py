from collections import Counter, namedtuple
from functools import cache
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    NewType,
    Optional,
    Set,
    Tuple,
)

import music_libs.Spotify as Spotify
import music_libs.Yandex as Yandex

my_Track = namedtuple(
    "Track",
    ["id", "name", "artists"],
    defaults=("0", "Empty title", "Empty artist"),
)
My_Track = NewType("My_Track", my_Track)
services_classes = {"yandex": Yandex.User, "spotify": Spotify.User}


class User(object):
    def __init__(self, user_ids: Dict[str, str]):
        self.accounts = {}
        for service in user_ids:
            user_id = user_ids[service]
            User = services_classes[service]
            self.accounts[service] = User(user_id)

    def call(self, method_name: str, kwargs_of_method: Dict | None = None) -> Set:
        if kwargs_of_method is None:
            kwargs_of_method = dict.fromkeys(self.accounts, {})
        results = set()
        for service in self.accounts:
            service_class = services_classes[service]
            if hasattr(service_class, method_name):
                method = getattr(service_class, method_name)
                result = method(self.accounts[service], kwargs_of_method)
                results.update(result)
        return results
