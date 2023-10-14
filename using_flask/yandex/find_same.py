from typing import NamedTuple, Set

import using_flask.yandex.get_user as get
from using_flask.yandex.get_user import User


def tracks(users: User) -> Set[NamedTuple]:
    same_tracks = users[0].raw_tracks()
    for user in users[1:]:
        user_tracks = user.raw_tracks()
        same_tracks &= user_tracks
    return set(get.track_obj.of(track) for track in same_tracks)


def artists(users: User) -> Set[str]:
    same_artists = users[0].artists()
    for user in users[1:]:
        user_artists = user.artists()
        same_artists &= user_artists
    return same_artists


def genres(users: User) -> Set[str]:
    same_genres = users[0].genres()
    for user in users[1:]:
        user_genres = user.genres()
        same_genres &= user_genres
    return same_genres
