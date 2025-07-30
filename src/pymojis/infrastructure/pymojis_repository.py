import json
import os
from random import sample
from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.domain.repositories.repository import PymojisRepository


class PymojisRepositoryImpl(PymojisRepository):
    def __init__(self, data_file_path: str | None = None):
        if data_file_path is None:
            base_dir = os.path.dirname(__file__)
            data_file_path = os.path.join(base_dir, "data", "emoji_data.json")

        if not os.path.exists(data_file_path):
            raise FileNotFoundError("No file found \n", data_file_path)
        self.data_file_path = data_file_path
        self.emojis: list[Emoji] = []
        self._load_data()

    def _load_data(self) -> None:
        try:
            with open(self.data_file_path, encoding="utf-8") as _file:
                data = json.load(_file)
                self.emojis = [
                    Emoji(
                        category=category,
                        name=emoji.get("name"),
                        code=emoji.get("code"),
                        emoji=emoji.get("emoji"),
                    )
                    for category, subcategories in data.get("emojis").items()
                    for emojis_list in subcategories.values()
                    for emoji in emojis_list
                ]

        except FileNotFoundError as file_not_found:
            raise FileNotFoundError(
                "No file found\n", file_not_found
            ) from FileNotFoundError

    def get_all(
        self, exclude: Literal["complex"] | list[Categories] | None
    ) -> list[Emoji]:
        all_emojis: list[Emoji] = []
        if not exclude:
            all_emojis = self.emojis.copy()
        else:
            for emoji in self.emojis:
                if exclude == "complex" and len(emoji.code) > 1:
                    continue
                if emoji.category.lower() in (excluded.lower() for excluded in exclude):
                    continue
                all_emojis.append(emoji)
        return all_emojis

    def get_by_category(self, category: Categories) -> list[str]:
        return [
            emoji.emoji
            for emoji in self.emojis
            if category.lower() == emoji.category.lower()
        ]

    def get_by_code(self, code: str) -> str | None:
        return next(
            (
                emoji.emoji
                for emoji in self.emojis
                if code in emoji.code and len(emoji.code) == 1
            ),
            None,
        )

    def get_by_name(self, name: str) -> str | None:
        return next(
            (
                emoji.emoji
                for emoji in self.emojis
                if emoji.name.lower() == name.lower()
            ),
            None,
        )

    def validate_emoji(self, code: str) -> list[str]:
        return [emoji.emoji for emoji in self.emojis if code in emoji.code]

    def get_random_emojis(
        self, category: Categories | None = None, length: int = 1
    ) -> list[Emoji]:
        emojis: list[Emoji] = self.emojis.copy()
        if category:
            emojis = [
                emoji
                for emoji in self.emojis
                if emoji.category.lower() == category.lower()
            ]
        return sample(emojis, min(length, len(emojis)))
