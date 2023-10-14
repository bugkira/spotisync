from collections import Counter, namedtuple
from functools import cache
from math import ceil
from multiprocessing import Pool
from typing import Any, Callable, Dict, List, NamedTuple, NewType, Optional, Set, Tuple

import yandex_music

client = yandex_music.Client()

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


class YandexUser(object):
    def __init__(self, user_id):
        self.id = user_id

    @cache
    def playlists(self) -> Dict[str, str]:
        """АХТУНГ: метод предполагает, что у пользователя нет плейлистов с одинаковым названием"""
        raw_playlists = {"Мне нравится": 3}
        for playlist in client.users_playlists_list(self.id):
            raw_playlists[playlist["title"]] = playlist["kind"]
        return raw_playlists

    @cache
    def raw_tracks(
        self, from_playlists: Tuple[str] = ("Мне нравится",)
    ) -> Set[My_Track]:
        ans = set()
        for playlist in from_playlists:
            if playlist != "Мне нравится":
                user_tracks = client.users_playlists(
                    self.playlists()[playlist], self.id
                ).tracks
                ans.update(user_tracks)
                continue
            user_tracks = client.users_likes_tracks(self.id)
            tracks_ids = [track.track_id for track in user_tracks]
            chunk_size = 125
            num_processes = ceil(len(user_tracks) / chunk_size)
            todos = partite(tracks_ids, chunk_size)
            with Pool(processes=num_processes) as pool:
                chunk_results = pool.map(client.tracks, todos)
                for results in chunk_results:
                    ans.update(results)
        return ans

    def method(name: str = "", ans_type=set) -> Callable:
        def two_inner(func: Callable) -> Callable:
            @cache
            def inner(
                self,
                from_playlists: Tuple[str] = ("Мне нравится",),
                *args,
                **kwargs,
            ) -> Optional:
                ans = ans_type()
                for res in map(
                    lambda x: magic(func(x, *args, **kwargs)),
                    self.raw_tracks(from_playlists),
                ):
                    ans.update(res)
                return ans

            inner.of = func
            if not hasattr(YandexUser, func.__name__):
                setattr(YandexUser, name or func.__name__, inner)
            return inner

        return two_inner

    def filter(name: str = "") -> Callable:
        def two_inner(checking: Callable) -> Callable:
            def inner(self, *args, **kwargs) -> Optional:
                ans = set(
                    map(
                        track_obj.of,
                        filter(
                            lambda track: checking(track, *args, **kwargs),
                            self.raw_tracks(),
                        ),
                    )
                )
                return ans

            inner.of = checking
            if not hasattr(YandexUser, checking.__name__):
                setattr(YandexUser, name or checking.__name__, inner)
            return inner

        return two_inner


@YandexUser.method()
def artists(track: dict) -> Set[str]:
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@YandexUser.method("tracks")
def track_obj(track: dict) -> NamedTuple:
    id_ = track["id"]
    name = track["title"]
    artists_ = tuple(artists.of(track))
    ans = my_Track(id_, name, artists_)
    return ans


@YandexUser.method(ans_type=Counter)
def genres(track: dict) -> Set[str]:
    genres = {album["genre"] for album in track["albums"]}
    return genres


@YandexUser.filter("tracks_with_genres")
def check_genres(track: dict, search_genres: Set = set()) -> bool:
    return bool(search_genres & genres.of(track))


@YandexUser.filter("tracks_by_artists")
def check_artists(track: dict, search_artists: Set = set()) -> bool:
    return bool(search_artists & artists.of(track))
