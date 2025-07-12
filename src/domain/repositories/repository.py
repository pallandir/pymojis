from abc import ABC, abstractmethod

from src.domain.entities.emojis import Categories, Emoji


class PymojisRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Emoji]:
        pass

    @abstractmethod
    def get_random_emoji(self):
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> str:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> str:
        pass

    @abstractmethod
    def get_by_category(self, category: Categories) -> list[str]:
        pass

    @abstractmethod
    def validate_emoji(self, code: str) -> str:
        pass
