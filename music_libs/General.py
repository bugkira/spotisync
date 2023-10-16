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
from music_libs.Base import My_Track
from music_libs.Base import User as BaseUser
from music_libs.Base import magic, my_Track, partite

services_classes = {"yandex": Yandex.User, "spotify": Spotify.User}


class User(BaseUser):
    def __init__(self, user_ids: Dict[str, str]):
        self.accounts = {}
        for service in user_ids:
            user_id = user_ids[service]
            User = services_classes[service]
            self.accounts[service] = User(user_id)

    def call(self, method_name: str, *args_of_method, **kwargs_of_method) -> Set:
        results = Counter()
        for service in self.accounts:
            service_class = services_classes[service]
            if hasattr(service_class, method_name):
                method = getattr(service_class, method_name)
                result = method(
                    self.accounts[service], *args_of_method, **kwargs_of_method
                )
                results.update(result)
        return results

    for method in BaseUser.__abstractmethods__:
        setattr(
            BaseUser,
            method,
            lambda self, *args, **kwargs: User.call(self, method, *args, **kwargs),
        )
