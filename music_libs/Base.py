import typing as t
from abc import ABC, abstractmethod
from collections import Counter, namedtuple
from functools import wraps
from math import ceil

MyTrack = namedtuple(
    "Track",
    ["id", "name", "artists"],
    defaults=("0", "Empty title", "Empty artist"),
)


def magic(obj: t.Any) -> set:
    """
    Преобразует объект-не множество в множество из объекта. Объект-множество не изменяется.

    Args:
        obj: Объект, который нужно преобразовать в множество.

    Returns:
        set: Множество, содержащее объект.
    """
    if isinstance(obj, set):
        return obj
    else:
        return {obj}


class MetaUser(ABC):
    interface_methods = [
        "artists",
        "filter",
        "genres",
        "method",
        "playlists",
        "raw_tracks",
        "tracks",
        "tracks_by_artists",
        "tracks_with_genres",
    ]

    def __init__(self, user_id):
        self.id = user_id

    @abstractmethod
    def playlists(self) -> t.Dict[str, str]:
        """
        Абстрактный метод для получения плейлистов пользователя.

        Returns:
            dict: Словарь вида {'название плейлиста': 'идентификатор плейлиста'}.
        """
        ...

    @abstractmethod
    def raw_tracks(
        self, from_playlists: str | t.Tuple[str] | None = None
    ) -> t.Set[MyTrack]:
        """
        Абстрактный метод для получения всех треков пользователя или треков из указанных плейлистов.

        Args:
            from_playlists: Идентификаторы плейлистов, из которых нужно получить треки.
                Если None, то треки будут получены из всех плейлистов пользователя.

        Returns:
            set: Множество треков пользователя.
        """
        ...

    @classmethod
    def method(cls, name: str = "", ans_type=set) -> t.Callable:
        """
        Декоратор для добавления методов работы с треками пользователя.
        Особенность декораторов method и filter в том,
        что оригинальная функция func остаётся доступной под названием 'func.of'.
        Название атрибута 'of' выбрано для большей схожести кода с естественным языком.
        Сравните: 'genres.of(track)' и 'genres.orig(track).

        Args:
            cls: Класс, в который добавляется метод. Нужно для того, чтобы метод добавлялся в наследника, а не в шаблон.
            name: Название метода. Если не указано, будет использовано имя оригинальной функции.
            ans_type: Тип данных, в котором будет возвращаться результат выполнения метода. По умолчанию - множество.

        Returns:
            Callable: Декорированная функция.
        """

        def two_inner(func: t.Callable) -> t.Callable:
            @wraps(func)
            def inner(
                self,
                from_playlists: t.Tuple[str] | None = None,
                *args,
                **kwargs,
            ) -> t.Optional:
                """
                Внутренняя функция метода, возвращающая результат выполнения оригинальной функции.

                Args:
                    self: Экземпляр класса MetaUser.
                    from_playlists: Идентификаторы плейлистов, из которых нужно получить треки.
                    *args: Дополнительные аргументы для оригинальной функции.
                    **kwargs: Дополнительные ключевые аргументы для оригинальной функции.

                Returns:
                    Optional: Результат выполнения оригинальной функции.
                """
                ans = ans_type()
                tracks = self.raw_tracks(from_playlists=from_playlists)
                # for res in map(
                #     lambda track: magic(func(track, *args, **kwargs)),
                #     tracks,
                # ):
                #     ans.update(res)
                for track in tracks:
                    res = magic(func(track, *args, **kwargs))
                    # print(res, end=", ")
                    ans.update(res)
                return ans

            inner.of = func
            # if not hasattr(MetaUser, func.__name__):
            #     setattr(MetaUser, name or func.__name__, inner)
            setattr(cls, name or func.__name__, inner)
            return inner

        return two_inner

    @classmethod
    def filter(cls, name: str = "") -> t.Callable:
        """
        Декоратор для добавления фильтров при работе с треками пользователя.
        Особенность декораторов method и filter в том,
        что оригинальная функция func остаётся доступной под названием 'func.of'.
        Название атрибута 'of' выбрано для большей схожести кода с естественным языком.
        Сравните: 'check_genres.of(track)' и 'check_genres.orig(track).

        Args:
            name: Название фильтра. Если не указано, будет использовано имя оригинальной функции.

        Returns:
            Callable: Декорированная функция.
        """

        def two_inner(checking: t.Callable) -> t.Callable:
            def inner(
                self,
                *args,
                from_playlists: t.Tuple[str] | None = None,
                **kwargs,
            ) -> t.Optional:
                """
                Внутренняя функция фильтра, возвращающая отфильтрованные треки.

                Args:
                    self: Экземпляр класса MetaUser.
                    args: Дополнительные аргументы для оригинальной функции.
                    from_playlists: Идентификаторы плейлистов, из которых нужно получить треки.
                    kwargs: Дополнительные ключевые аргументы для оригинальной функции.

                Returns:
                    Optional: Отфильтрованные треки пользователя.
                """
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
            # if not hasattr(MetaUser, checking.__name__):
            setattr(cls, name or checking.__name__, inner)
            return inner

        return two_inner


@MetaUser.method(ans_type=Counter)
def artists(track: dict) -> t.Set[str]:
    """
    Функция для получения артистов трека.

    Args:
        track: Трек в формате dict.

    Returns:
        set: Множество артистов трека.
    """
    artists = {artist["name"] for artist in track["artists"]}
    return artists


@MetaUser.method("tracks")
def track_obj(track: dict) -> t.NamedTuple:
    """
    Функция для преобразования трека в объект MyTrack.

    Args:
        track: "Сырой" трек в формате JSON.

    Returns:
        MyTrack: Объект трека.
    """
    ...


@MetaUser.method(ans_type=Counter)
def genres(track: dict) -> t.Set[str]:
    """
    Функция для получения жанров трека.

    Args:
        track: "Сырой" трек в формате JSON.

    Returns:
        set: Множество жанров трека.
    """
    ...


@MetaUser.filter("tracks_with_genres")
def check_genres(track: dict, search_genres: t.Iterable) -> bool:
    """
    Функция-фильтр для проверки наличия указанных жанров у трека.

    Args:
        track: "Сырой" трек в формате JSON.
        search_genres: Итерируемый объект со списком жанров для проверки.

    Returns:
        bool: Результат проверки на наличие указанных жанров у трека.
    """

    track_genres = genres.of(track)
    for genre in search_genres:
        if genre in track_genres:
            return True
    return False


@MetaUser.filter("tracks_by_artists")
def check_artists(track: dict, search_artists: t.Iterable) -> bool:
    """Функция-фильтр для проверки наличия указанных артистов у трека.

    Args:
        track: "Сырой" трек в формате JSON.
        search_artists: Итерируемый объект со списком артистов для проверки.

    Returns:
        bool: Результат проверки на наличие указанных артистов у трека.
    """
    track_artists = artists.of(track)
    for artist in search_artists:
        if artist in track_artists:
            return True
    return False
