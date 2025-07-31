from abc import ABC, abstractmethod
from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji


class PymojisRepository(ABC):
    @abstractmethod
    def get_all(
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]:
        pass

    @abstractmethod
    def get_random_emojis(
        self,
        categories: list[Categories] | None = None,
        length: int = 1,
        exclude: Literal["complex"] | list[Categories] | None = None,
    ) -> list[Emoji]:
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> str | None:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> str | None:
        pass

    @abstractmethod
    def get_by_category(self, category: Categories) -> list[str]:
        pass

    @abstractmethod
    def get_by_emoji(self, emoji: str) -> Emoji | None:
        pass

    @abstractmethod
    def contains_emojis(self, text: str) -> bool:
        pass

    @abstractmethod
    def is_emoji(self, text: str) -> bool:
        pass

    @abstractmethod
    def emojifie(self, text: str) -> str:
        pass
