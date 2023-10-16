from abc import ABC, abstractmethod
from collections import Counter, namedtuple
from math import ceil
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

my_Track = namedtuple(
    "Track",
    ["id", "name", "artists"],
    defaults=("0", "Empty title", "Empty artist"),
)
My_Track = NewType("My_Track", my_Track)


def magic(obj: Any) -> Set:
    if isinstance(obj, set):
        return obj
    else:
        return {obj}


def partite(lst: list, chunk_size: int) -> List[List]:
    ans = []
    for i in range(ceil(len(lst) / chunk_size)):
        ans.append(lst[i * chunk_size : (i + 1) * chunk_size])
    return ans


class User(ABC):
    def __init__(self, user_id):
        self.id = user_id

    @abstractmethod
    def playlists(self) -> Dict[str, str]:
        """АХТУНГ: метод предполагает, что у пользователя нет плейлистов с одинаковым названием"""
        pass

    @abstractmethod
    def raw_tracks(self, from_playlists: Tuple[str] | None = None) -> Set[My_Track]:
        pass

    def method(name: str = "", ans_type=set) -> Callable:
        def two_inner(func: Callable) -> Callable:
            def inner(
                self,
                from_playlists: Tuple[str] | None = None,
                *args,
                **kwargs,
            ) -> Optional:
                ans = ans_type()
                tracks = self.raw_tracks(from_playlists=from_playlists)
                for res in map(
                    lambda track: magic(func(track, *args, **kwargs)),
                    tracks,
                ):
                    ans.update(res)
                return ans

            inner.of = func
            if not hasattr(User, func.__name__):
                setattr(User, name or func.__name__, inner)
            return inner

        return two_inner

    def filter(name: str = "") -> Callable:
        def two_inner(checking: Callable) -> Callable:
            def inner(
                self,
                *args,
                from_playlists: Tuple[str] | None = None,
                **kwargs,
            ) -> Optional:
                tracks = self.raw_tracks(from_playlists=from_playlists)
                ans = set(
                    map(
                        track_obj.of,
                        filter(
                            lambda track: checking(track, *args, **kwargs),
                            tracks,
                        ),
                    )
                )
                return ans

            inner.of = checking
            if not hasattr(User, checking.__name__):
                setattr(User, name or checking.__name__, inner)
            return inner

        return two_inner

        @abstractmethod
        def genres(self):
            pass

        @abstractmethod
        def artists(self):
            pass

        @abstractmethod
        def tracks(self):
            pass


@User.method("tracks")
def track_obj(track: dict) -> NamedTuple:
    pass
