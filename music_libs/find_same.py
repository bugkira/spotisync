from typing import List, NamedTuple, Set, Union

from music_libs import Spotify, Yandex

User = Union[Yandex.User, Spotify.User]
# from music_libs.Yandex import User


def prepare_users(func):
    def inner(*lst_users):
        # users = []
        # for user in lst_users:
        #     users += list(user.accounts.values())
        users = lst_users
        return func(users)

    return inner


@prepare_users
def tracks(users: List[User]) -> Set[NamedTuple]:
    same_tracks = users[0].tracks()
    for user in users[1:]:
        user_tracks = user.tracks()
        same_tracks &= user_tracks
    return same_tracks


@prepare_users
def artists(users: List[User]) -> Set[str]:
    same_artists = users[0].artists()
    for user in users[1:]:
        user_artists = user.artists()
        same_artists &= user_artists
    return set(same_artists)


@prepare_users
def genres(users: List[User]) -> Set[str]:
    same_genres = users[0].genres()
    for user in users[1:]:
        user_genres = user.genres()
        same_genres &= user_genres
    return set(same_genres)
