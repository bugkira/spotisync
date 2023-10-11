from typing import NamedTuple, Set

from using_flask.get_user import User


def tracks(*users: User) -> Set[NamedTuple]:
    same_tracks = users[0].tracks()
    for user in users[1:]:
        user_tracks = user.tracks()

        same_tracks &= user_tracks
    return same_tracks


def artists(*users: User) -> Set[str]:
    same_artists = users[0].artists()
    for user in users[1:]:
        user_artists = user.artists()
        same_artists &= user_artists
    return same_artists
