from typing import NamedTuple, Set

from using_flask.get_user import User


def tracks(*users_ids: str) -> Set[NamedTuple]:
    same_tracks = User(users_ids[0]).tracks()
    for user_id in users_ids[1:]:
        user_tracks = User(user_id).tracks()

        same_tracks &= user_tracks
    return same_tracks


def artists(*users_ids: str) -> Set[str]:
    same_artists = User(users_ids[0]).artists()
    for user_id in users_ids[1:]:
        user_artists = User(user_id).artists()
        same_artists &= user_artists
    return same_artists
