from collections import Counter, namedtuple
from functools import cache
from math import ceil
from multiprocessing import Pool
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


class User(object):
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
    def raw_tracks(self, from_playlists: Tuple[str] | None = None) -> Set[My_Track]:
        if from_playlists is None:
            # from_playlists = ("Мне нравится",)
            from_playlists = tuple(self.playlists())
            return self.raw_tracks(from_playlists=from_playlists)
        ans = set()
        for playlist in from_playlists:
            if playlist != "Мне нравится":
                too_row_tracks = client.users_playlists(
                    self.playlists()[playlist], self.id
                ).tracks
                raw_tracks = {
                    too_raw_track["track"] for too_raw_track in too_row_tracks
                }
                ans.update(raw_tracks)
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
            if not hasattr(User, checking.__name__):
                setattr(User, name or checking.__name__, inner)
            return inner

        return two_inner


@User.method(ans_type=Counter)
def artists(track: dict) -> Set[str]:
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@User.method("tracks")
def track_obj(track: dict) -> NamedTuple:
    id_ = track["id"]
    name = track["title"]
    artists_ = tuple(artists.of(track))
    ans = my_Track(id_, name, artists_)
    return ans


@User.method(ans_type=Counter)
def genres(track: dict) -> Set[str]:
    genres = {album["genre"] for album in track["albums"]}
    return genres


@User.filter("tracks_with_genres")
def check_genres(track: dict, search_genres: Iterable) -> bool:
    track_genres = genres.of(track)
    for genre in search_genres:
        if genre in track_genres:
            return True
    return False


@User.filter("tracks_by_artists")
def check_artists(track: dict, search_artists: Iterable) -> bool:
    track_artists = artists.of(track)
    for artist in search_artists:
        if artist in track_artists:
            return True
    return False
