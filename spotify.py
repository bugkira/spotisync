from collections import namedtuple
from typing import NamedTuple, Set

import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "2051998dbe874955959db45e2ec13e19"
CLIENT_SECRET = "169105320d2042ba97938f16e2947f85"
RED_URI = "https://developer.spotify.com/dashboard"

scope = (
    "playlist-read-private"  # разрешение на чтение приватных плейлистов пользователя
)

auth_manager = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, RED_URI, scope=scope)
sp = spotipy.Spotify(auth_manager=auth_manager)
my_Track = namedtuple(
    "Track",
    ["name", "artists"],
    defaults=("Empty title", ["Empty artist"]),
)


def get_user_tracks(user_id: str) -> Set[NamedTuple]:
    playlists = sp.user_playlists(user_id)
    answer = set()
    for playlist in playlists["items"]:
        results = sp.playlist_items(playlist["id"])
        for item in results["items"]:
            name = item["track"]["name"]
            artists = tuple(artist["name"] for artist in item["track"]["artists"])
            track = my_Track(name, artists)
            answer.add(track)
    return answer


def find_same_tracks(user_id_1: str, user_id_2: str) -> Set[NamedTuple]:
    tracks_1 = get_user_tracks(user_id_1)
    tracks_2 = get_user_tracks(user_id_2)
    return tracks_1 & tracks_2


def get_user_artists(user_id: str) -> Set[str]:
    playlists = sp.user_playlists(user_id)
    answer = set()
    for playlist in playlists["items"]:
        results = sp.playlist_items(playlist["id"])
        for track in results["items"]:
            artists = track["track"]["artists"]
            answer |= {x["name"] for x in artists}
    return answer


def find_same_artists(user_id_1: str, user_id_2: str) -> Set[str]:
    artists_1 = get_user_artists(user_id_1)
    artists_2 = get_user_artists(user_id_2)
    return artists_1 & artists_2


if __name__ == "__main__":
    petya = "315adko2dqldbbcft3poddigg5ua"
    kira = "31yzohqcua2qiocawfw5536demti"
    print(find_same_tracks(petya, kira))
    print(find_same_artists(petya, kira))
