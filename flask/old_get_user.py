from collections import namedtuple
from functools import cache, reduce
from typing import Callable, Dict, Iterable, NamedTuple, NewType, Optional, Set, Type

from yandex_music import Client

# client = Client("y0_AgAAAABaiLCNAAG8XgAAAADuVh7_ztNypsyJSTuG_jS9sn_HBn8ICM4")
client = Client()
my_Track = namedtuple(
    "Track",
    ["name", "artists"],
    defaults=("Empty title", ("Empty artist")),
)
My_Track = NewType("My_Track", my_Track)


class Counter(dict):
    def __init__(self, lst=[]):
        self.dct = {}
        if lst:
            for i in lst:
                self.add(i)

    def add(self, elem):
        self.dct[elem] = self.dct.get(elem, 0) + 1

    def sorted_(self):
        return dict(
            sorted(
                self.dct.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    def __ior__(self, other: Iterable):
        for elem in other:
            self.add(elem)
        return self

    def __repr__(self):
        return self.sorted_()

    def __str__(self):
        return str(self.__repr__())


Counter_ = NewType("Counter_", Counter)

# def based_on_user(func: Callable) -> Callable:
#     return lambda user_id: func(user_tracks(user_id))


@cache
def user_tracks(user_id: str):
    print(user_id, "IS CHECKING")
    user_tracks = client.users_likes_tracks(user_id)
    tracks_ids = [track.track_id for track in user_tracks]
    user_tracks = client.tracks(tracks_ids)
    return user_tracks


def based_on_tracks(
    ans_type: type = set,
    method: Callable = lambda x, y: x.__ior__(y),
) -> Callable:
    def inner(func: Callable) -> Callable:
        def ultra_inner(user_id: str) -> Optional:
            ans = ans_type()
            for track in user_tracks(user):
                method(ans, func(track))
            return ans

        return ultra_inner

    return inner


@based_on_tracks()
def tracks(track: dict) -> NamedTuple:
    name = track["title"]
    artists = tuple(artist["name"] for artist in track["artists"])
    ans = my_Track(name, artists)
    # print(ans)
    return ans


@based_on_tracks()
def artists(track: dict) -> Set[str]:
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@based_on_tracks(ans_type=Counter)
def genres(track: dict) -> Dict[str, int]:
    genres = {album["genre"] for album in track["albums"]}
    return genres


if __name__ == "__main__":
    from time import time

    user = "kirabagaev"
    f = lambda x: x
    g = based_on_tracks(f)
    print(genres(user))
    start = time()
    user_tracks("newbugsbunny")
    end = time()
    print(start - end)


# список треков определенного жанра
# поиск исполнителя в списке
