from collections import Counter, namedtuple
from functools import cache, cached_property
from typing import Callable, NamedTuple, NewType, Optional, Set

import yandex_music

client = yandex_music.Client()
my_Track = namedtuple(
    "Track",
    ["id", "name", "artists"],
    defaults=("0", "Empty title", ("Empty artist")),
)
My_Track = NewType("My_Track", my_Track)


def magic(obj):
    if isinstance(obj, set):
        return obj
    else:
        return {obj}


class User(object):
    def __init__(self, user_id):
        self.id = user_id

    @cached_property
    def raw_tracks(self):
        user_tracks = client.users_likes_tracks(self.id)
        tracks_ids = {track.track_id for track in user_tracks}
        user_tracks = set(client.tracks(tracks_ids))
        return user_tracks

    def method(name: str = "", ans_type=set) -> Callable:
        def two_inner(func: Callable) -> Callable:
            def inner(self, *args, **kwargs) -> Optional:
                ans = ans_type()
                for res in map(
                    lambda x: magic(func(x, *args, **kwargs)),
                    self.raw_tracks,
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
            def inner(self, *args, **kwargs) -> Optional:
                ans = set(
                    map(
                        track_obj.of,
                        filter(
                            lambda track: checking(track, *args, **kwargs),
                            self.raw_tracks,
                        ),
                    )
                )
                return ans

            inner.of = checking
            if not hasattr(User, checking.__name__):
                setattr(User, name or checking.__name__, inner)
            return inner

        return two_inner


@User.method("tracks")
def track_obj(track: dict) -> NamedTuple:
    id_ = track["id"]
    name = track["title"]
    artists = tuple(artist["name"] for artist in track["artists"])
    ans = my_Track(id_, name, artists)
    return ans


@User.method()
def artists(track: dict) -> Set[str]:
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@User.method(ans_type=Counter)
def genres(track: dict) -> Set[str]:
    genres = {album["genre"] for album in track["albums"]}
    return genres


@User.filter("tracks_with_genres")
def check_genres(track: dict, search_genres: Set = set()) -> bool:
    return bool(search_genres & genres.of(track))


@User.filter("tracks_with_artists")
def check_artists(track: dict, search_artists: Set = set()) -> bool:
    return bool(search_artists & artists.of(track))
