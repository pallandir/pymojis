from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji


class PymojisRepository(ABC):
    @abstractmethod
    def get_all(
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]: ...

    @abstractmethod
    def get_random_emojis(
        self,
        categories: list[Categories] | None = None,
        length: int = 1,
        exclude: Literal["complex"] | list[Categories] | None = None,
    ) -> list[Emoji]: ...

    @abstractmethod
    def get_by_code(self, code: str) -> str | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> str | None: ...

    @abstractmethod
    def get_by_category(self, category: Categories) -> list[str]: ...

    @abstractmethod
    def get_by_emoji(self, emoji: str) -> Emoji | None: ...

    @abstractmethod
    def contains_emojis(self, text: str) -> bool: ...

    @abstractmethod
    def is_emoji(self, text: str) -> bool: ...

    @abstractmethod
    def emojifie(self, text: str) -> str: ...

    @abstractmethod
    def to_html(self, emoji: str) -> str: ...

    @abstractmethod
    def extract(self, text: str) -> list[Emoji]: ...

    @abstractmethod
    def find(self, text: str) -> Iterator[tuple[Emoji, int, int]]: ...

    @abstractmethod
    def count(self, text: str) -> int: ...

    @abstractmethod
    def count_by(self, text: str) -> dict[Emoji, int]: ...

    @abstractmethod
    def strip(self, text: str) -> str: ...

    @abstractmethod
    def replace(self, text: str, repl: str | Callable[[Emoji], str]) -> str: ...

    @abstractmethod
    def demojifie(self, text: str) -> str: ...

    @abstractmethod
    def to_codepoint_string(
        self, emoji: str, sep: str = " ", prefix: str = "U+"
    ) -> str: ...

    @abstractmethod
    def to_unicode_escape(self, emoji: str) -> str: ...

    @abstractmethod
    def to_image_url(
        self,
        emoji: str,
        provider: Literal["twemoji", "openmoji"] = "twemoji",
        extension: Literal["svg", "png"] = "svg",
    ) -> str: ...

    @abstractmethod
    def to_shortcode(self, emoji: str, set_name: str = "github") -> str | None: ...

    @abstractmethod
    def from_shortcode(self, code: str, set_name: str | None = None) -> str | None: ...

    @abstractmethod
    def base_of(self, emoji: str) -> str | None: ...

    @abstractmethod
    def skin_tones(self, emoji: str) -> list[str]: ...

    @abstractmethod
    def is_flag(self, emoji: str) -> bool: ...

    @abstractmethod
    def flag_for(self, country_code: str) -> str: ...

    @abstractmethod
    def country_of(self, emoji: str) -> str | None: ...

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[Emoji]: ...

    @abstractmethod
    def suggest(self, emoji: str, limit: int = 5) -> list[Emoji]: ...

    @abstractmethod
    def categories(self) -> list[str]: ...

    @abstractmethod
    def sub_categories(self, category: str | None = None) -> list[str]: ...

    @abstractmethod
    def get_by_subcategory(self, name: str) -> list[Emoji]: ...
