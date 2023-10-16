from collections import Counter
from functools import cache
from math import ceil
from multiprocessing import Pool
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

import spotipy
from music_libs.Base import My_Track
from music_libs.Base import User as BaseUser
from music_libs.Base import magic, my_Track, partite
from music_libs.credentials import CLIENT_ID, CLIENT_SECRET, RED_URI
from spotipy.oauth2 import SpotifyOAuth

auth_manager = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, RED_URI)
sp = spotipy.Spotify(auth_manager=auth_manager)


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
    too_raw_tracks = sp.playlist_items(**kwargs_)["items"]
    ans = [too_raw_track["track"] for too_raw_track in too_raw_tracks]
    return ans


class User(BaseUser):
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
            from_playlists = tuple(self.playlists())
            return self.raw_tracks(from_playlists=from_playlists)

        playlists = {}
        for name in from_playlists:
            playlist = self.playlists()[name]
            playlists[name] = playlist
        tracks_amount = sum(playlist["total"] for playlist in playlists.values())
        chunk_size = 125
        num_processes = ceil(tracks_amount / chunk_size)
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
    name = track["name"]
    artists_ = tuple(artists.of(track))
    ans = my_Track(id_, name, artists_)
    return ans


@User.method(ans_type=Counter)
def genres(track: dict) -> Set[str]:
    genres = set()
    for artist in track["artists"]:
        genres |= set(sp.artist(artist["id"])["genres"])
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
