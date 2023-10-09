from typing import NamedTuple, Set

import get_user
from get_user import User


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


if __name__ == "__main__":
    user1 = User("kirabagaev")
    user2 = User("newbugsbunny")
    # tracks = get_user_tracks(user2_id)
    tracks = tracks(user1, user2)
    print("Общие треки:")
    for track in tracks:
        print(track)
    # artists = artists(user1_id, user2_id)
    # print("Общие артисты:")
    # print(*artists, sep=", ")
