from collections import Counter, namedtuple
from functools import cache
from math import ceil
from multiprocessing import Pool
from typing import Any, Callable, Dict, List, NamedTuple, NewType, Optional, Set, Tuple

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# from typing import *
from using_flask.spotify.credentials import CLIENT_ID, CLIENT_SECRET, RED_URI

auth_manager = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, RED_URI)
sp = spotipy.Spotify(auth_manager=auth_manager)

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


def chunkify_playlists(playlists, chunk_size):
    ans = []
    for playlist in playlists.values():
        playlist_size = playlist["total"]
        chunks_amount = ceil(playlist_size / chunk_size)
        for k in range(chunks_amount):
            ans.append((playlist, k, chunk_size))
    return ans


def get_playlist_tracks(args_: Tuple[Dict, int, int]) -> List[Dict]:
    playlist, chunk_number, chunk_size = args_
    kwargs_ = {}
    kwargs_["playlist_id"] = playlist["id"]
    kwargs_["limit"] = min(chunk_size, playlist["total"])
    kwargs_["offset"] = chunk_size * chunk_number
    kwargs_["fields"] = ["items"]
    ans = sp.playlist_items(**kwargs_)["items"]
    return ans


class SpotifyUser(object):
    def __init__(self, user_id):
        self.id = user_id

    @cache
    def playlists(self) -> Dict[str, str]:
        """АХТУНГ: метод предполагает, что у пользователя нет плейлистов с одинаковым названием"""
        raw_playlists = {}
        for playlist in sp.user_playlists(self.id)["items"]:
            raw_playlists[playlist["name"]] = {
                "id": playlist["id"],
                "total": playlist["tracks"]["total"],
            }
        return raw_playlists

    @cache
    def raw_tracks(self, from_playlists: Tuple[str] | None = None) -> Set[My_Track]:
        if from_playlists is None:
            playlists = self.playlists()
        else:
            # playlists = [self.playlists()[name] for name in from_playlists]
            playlists = {}
            for name in from_playlists:
                playlist = self.playlists()[name]
                playlists[name] = playlist
        tracks_amount = sum(playlist["total"] for playlist in playlists.values())
        chunk_size = 125

        num_processes = ceil(tracks_amount / chunk_size)
        # user_tracks = set()
        user_tracks = []
        with Pool(processes=num_processes) as pool:
            chunk_results = pool.map(
                get_playlist_tracks,
                chunkify_playlists(playlists, chunk_size),
            )
            for results in chunk_results:
                # user_tracks.update(results)
                user_tracks += results
        return user_tracks

    def method(name: str = "", ans_type=set) -> Callable:
        def two_inner(func: Callable) -> Callable:
            def inner(
                self,
                from_playlists: Tuple[str] | None = None,
                *args,
                **kwargs,
            ) -> Optional:
                if from_playlists is None:
                    from_playlists = self.playlists()
                ans = set()
                for playlist_name in from_playlists:
                    results = self.raw_tracks(from_playlists=(playlist_name,))
                    for res in map(
                        lambda x: magic(func(x["track"], *args, **kwargs)),
                        results,
                    ):
                        ans.update(res)
                # results = self.raw_tracks(from_playlists=from_playlists)
                # for res in map(
                #     lambda x: magic(func(x["track"], *args, **kwargs)),
                #     results,
                # ):
                #     ans.update(res)
                return ans

            inner.of = func
            if not hasattr(SpotifyUser, func.__name__):
                setattr(SpotifyUser, name or func.__name__, inner)
            return inner

        return two_inner


@SpotifyUser.method()
def artists(track: dict) -> Set[str]:
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@SpotifyUser.method("tracks")
def track_obj(track: dict) -> NamedTuple:
    id_ = track["id"]
    name = track["name"]
    artists_ = tuple(artists.of(track))
    ans = my_Track(id_, name, artists_)
    return ans
