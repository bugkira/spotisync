from abc import ABC, abstractmethod
from collections import Counter, namedtuple
from functools import wraps
from math import ceil
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

MyTrack = namedtuple(
    "Track",
    ["id", "name", "artists"],
    defaults=("0", "Empty title", "Empty artist"),
)
pseudo_track_for_mock = {
    "id": "ID",
    "title": "TITLE",
    "albums": [{"genre": "GENRE"}],
    "artists": [{"name": "NAME"}],
}


def magic(obj: Any) -> set:
    """Преобразует объект-не множество в множество из объекта. Объект-множество не изменяется."""
    if isinstance(obj, set):
        return obj
    else:
        return {obj}


def partite(lst: list, chunk_size: int) -> List[List]:
    ans = []
    for i in range(ceil(len(lst) / chunk_size)):
        ans.append(lst[i * chunk_size : (i + 1) * chunk_size])
    return ans


class MetaUser(ABC):
    def __init__(self, user_id):
        self.id = user_id

    @abstractmethod
    def playlists(self) -> Dict[str, str]:
        ...

    @abstractmethod
    def raw_tracks(
        self, from_playlists: str | Tuple[str] | None = None
    ) -> Set[MyTrack]:
        ...

    @classmethod
    def method(cls, name: str = "", ans_type=set) -> Callable:
        """Декоратор для добавления методов работы с треками пользователя.

        Особенность декораторов method и filter в том,
        что оригинальная функция func остаётся доступной под названием 'func.of'.
        Название атрибута 'of' выбрано для большей схожести кода с естественным языком.
        Сравните: 'genres.of(track)' и 'genres.orig(track)."""

        def two_inner(func: Callable) -> Callable:
            @wraps(func)
            def inner(
                self,
                from_playlists: Tuple[str] | None = None,
                *args,
                **kwargs,
            ) -> Optional:
                ans = ans_type()
                tracks = self.raw_tracks(from_playlists=from_playlists)
                # for res in map(
                #     lambda track: magic(func(track, *args, **kwargs)),
                #     tracks,
                # ):
                #     ans.update(res)
                for track in tracks:
                    res = magic(func(track, *args, **kwargs))
                    # print(res, end=", ")
                    ans.update(res)
                return ans

            inner.of = func
            # if not hasattr(MetaUser, func.__name__):
            #     setattr(MetaUser, name or func.__name__, inner)
            setattr(cls, name or func.__name__, inner)
            return inner

        return two_inner

    @classmethod
    def filter(cls, name: str = "") -> Callable:
        """Декоратор для добавления фильтров при работе с треками пользователя.

        Особенность декораторов method и filter в том,
        что оригинальная функция func остаётся доступной под названием 'func.of'.
        Название атрибута 'of' выбрано для большей схожести кода с естественным языком.
        Сравните: 'check_genres.of(track)' и 'check_genres.orig(track)."""

        def two_inner(checking: Callable) -> Callable:
            def inner(
                self,
                *args,
                from_playlists: Tuple[str] | None = None,
                **kwargs,
            ) -> Optional:
                ans = set(
                    map(
                        track_obj.of,
                        filter(
                            lambda track: checking(track, *args, **kwargs),
                            self.raw_tracks(from_playlists),
                        ),
                    )
                )
                return ans

            inner.of = checking
            # if not hasattr(MetaUser, checking.__name__):
            setattr(cls, name or checking.__name__, inner)
            return inner

        return two_inner


@MetaUser.method(ans_type=Counter)
def artists(track: dict) -> Set[str]:
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@MetaUser.method("tracks")
def track_obj(track: dict) -> NamedTuple:
    ...


@MetaUser.method(ans_type=Counter)
def genres(track: dict) -> Set[str]:
    ...


@MetaUser.filter("tracks_with_genres")
def check_genres(track: dict, search_genres: Iterable) -> bool:
    track_genres = genres.of(track)
    for genre in search_genres:
        if genre in track_genres:
            return True
    return False


@MetaUser.filter("tracks_by_artists")
def check_artists(track: dict, search_artists: Iterable) -> bool:
    track_artists = artists.of(track)
    for artist in search_artists:
        if artist in track_artists:
            return True
    return False
