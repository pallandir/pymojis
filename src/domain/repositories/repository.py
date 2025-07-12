from abc import ABC, abstractmethod
from typing import Literal

from src.domain.entities.emojis import Categories, Emoji


class PymojisRepository(ABC):
    @abstractmethod
    def get_all(self, exclude: Literal["complex"] | list[Categories]) -> list[Emoji]:
        pass

    @abstractmethod
    def get_random_emojis(
        self, category: Categories | None = None, length: int = 1
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
    def validate_emoji(self, code: str) -> list[str]:
        pass
