import typing as t

import music_libs.Spotify as Spotify
import music_libs.Yandex as Yandex
from music_libs.Base import MetaUser

services_classes = {"yandex": Yandex.User, "spotify": Spotify.User}


class User(MetaUser):
    def __init__(self, user_ids: t.Dict[str, str]):
        self.accounts = {}
        for service in user_ids:
            user_id = user_ids[service]
            User = services_classes[service]
            self.accounts[service] = User(user_id)

    def __getattribute__(self, attr_name):
        if attr_name in MetaUser.interface_methods:
            return lambda *args, **kwargs: self.call(attr_name, **kwargs)
        else:
            return object.__getattribute__(self, attr_name)

    def __getitem__(self, service):
        return self.accounts[service]

    def call(
        self, method_name: str, kwargs_of_method: t.Dict[str, t.Dict] | None = None
    ) -> set:
        if kwargs_of_method is None:
            kwargs_of_method = dict.fromkeys(self.accounts, {})
        results = set()
        for service in self.accounts:
            method = getattr(self.accounts[service], method_name)
            result = method(**kwargs_of_method[service])
            results.update(result)
        return results

    def playlists(*args, **kwargs):
        """Этот метод существует только потому, что в шаблоне он абстрактен. Не используйте его."""

        raise NotImplementedError(
            "Этот метод существует только потому, что в шаблоне он абстрактен. Не используйте его. Как вы вообще сюда добрались?"
        )

    def raw_tracks(*args, **kwargs):
        """Этот метод существует только потому, что в шаблоне он абстрактен. Не используйте его."""
        raise NotImplementedError(
            "Этот метод существует только потому, что в шаблоне он абстрактен. Не используйте его. Как вы вообще сюда добрались?"
        )
