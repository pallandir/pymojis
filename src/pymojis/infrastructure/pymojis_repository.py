import json
import os
from random import sample
from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.domain.repositories.repository import PymojisRepository

from .utils import check_type, should_exclude


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
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]:
        all_emojis: list[Emoji] = []
        if not exclude:
            all_emojis = self.emojis.copy()
        else:
            for emoji in self.emojis:
                if should_exclude(emoji, exclude):
                    continue
                all_emojis.append(emoji)
        return all_emojis

    def get_by_category(self, category: Categories) -> list[str]:
        if not check_type(category, Categories):
            return []
        return [
            emoji.emoji
            for emoji in self.emojis
            if category.lower() == emoji.category.lower()
        ]

    def get_by_code(self, code: str) -> str | None:
        if not check_type(code, str):
            return None
        return next(
            (
                emoji.emoji
                for emoji in self.emojis
                if code.lower() in (emoji_code.lower() for emoji_code in emoji.code)
                and len(emoji.code) == 1
            ),
            None,
        )

    def get_by_name(self, name: str) -> str | None:
        if not check_type(name, str):
            return None
        return next(
            (
                emoji.emoji
                for emoji in self.emojis
                if emoji.name.lower() == name.lower()
            ),
            None,
        )

    def validate_emoji(self, code: str) -> list[str]:
        return [
            emoji.emoji
            for emoji in self.emojis
            if code.lower() in (emoji_code.lower() for emoji_code in emoji.code)
        ]

    def get_random_emojis(
        self,
        categories: list[Categories] | None = None,
        length: int = 1,
        exclude: Literal["complex"] | list[Categories] | None = None,
    ) -> list[Emoji]:
        emojis: list[Emoji] = []
        if categories:
            emojis = [
                emoji
                for emoji in self.emojis
                if emoji.category.lower()
                in (category.lower() for category in categories)
            ]
        if exclude:
            for emoji in self.emojis:
                if should_exclude(emoji, exclude):
                    continue
                emojis.append(emoji)
        else:
            emojis = self.emojis.copy()
        return sample(emojis, min(length, len(emojis)))
