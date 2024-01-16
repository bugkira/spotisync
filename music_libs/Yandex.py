import typing as t
from collections import Counter
from functools import cache
from math import ceil
from multiprocessing import Pool

import yandex_music
from music_libs.Base import MetaUser, MyTrack, artists

client = yandex_music.Client()


def split_into_chunks(lst: list, chunk_size: int) -> t.List[t.List]:
    """
    Разбивает список на фрагменты-подсписки заданного размера.

    Args:
        lst: Список, который нужно разбить.
        chunk_size: Размер подсписков.

    Returns:
        list: Список подсписков заданного размера.
    """
    ans = []
    for i in range(ceil(len(lst) / chunk_size)):
        ans.append(lst[i * chunk_size : (i + 1) * chunk_size])
    return ans


class User(MetaUser):
    @cache
    def playlists(self) -> t.Dict[str, int]:
        raw_playlists = {"Мне нравится": 3}
        for playlist in client.users_playlists_list(self.id):
            raw_playlists[playlist["title"]] = playlist["kind"]
        return raw_playlists

    @cache
    def raw_tracks(
        self, from_playlists: str | t.Tuple[str] | None = None
    ) -> t.Set[MyTrack]:
        match from_playlists:
            case None:
                from_playlists = ("Мне нравится",)
                return self.raw_tracks(from_playlists=from_playlists)
            case "all":
                from_playlists = tuple(self.playlists())
                return self.raw_tracks(from_playlists=from_playlists)

        ans = set()
        for playlist in from_playlists:
            # print(playlist, from_playlists)
            if playlist != "Мне нравится":
                too_raw_tracks = client.users_playlists(
                    self.playlists()[playlist], self.id
                ).tracks
                raw_tracks = {
                    too_raw_track["track"] for too_raw_track in too_raw_tracks
                }
                ans.update(raw_tracks)
                continue
            user_tracks = client.users_likes_tracks(self.id)
            tracks_ids = [track.track_id for track in user_tracks]
            chunk_size = 125
            num_processes = ceil(len(user_tracks) / chunk_size)
            todos = split_into_chunks(tracks_ids, chunk_size)
            with Pool(processes=num_processes) as pool:
                chunk_results = pool.map(client.tracks, todos)
                for results in chunk_results:
                    ans.update(results)
        return ans


@User.method("tracks")
def track_obj(track: dict) -> t.NamedTuple:
    id_ = track["id"]
    name = track["title"]
    artists_ = tuple(artists.of(track))
    ans = MyTrack(id_, name, artists_)
    return ans


@User.method(ans_type=Counter)
def genres(track: dict) -> t.Set[str]:
    genres = {album["genre"] for album in track["albums"]}
    return genres
