import json
import os
import re
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
                        sub_category=subcategory,
                        name=emoji.get("name"),
                        code=emoji.get("code"),
                        emoji=emoji.get("emoji"),
                    )
                    for category, subcategories in data.get("emojis").items()
                    for subcategory, emojis_list in subcategories.items()
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
        if not check_type(category, str):
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

    def get_by_emoji(self, emoji: str) -> Emoji | None:
        found_emoji = None
        for current_emoji in self.emojis:
            if current_emoji.emoji == emoji:
                found_emoji = current_emoji
                break

        return found_emoji

    def contains_emojis(self, text: str) -> bool:
        for emoji in self.emojis:
            if emoji.emoji in text:
                return True
        return False

    def is_emoji(self, text: str) -> bool:
        if not check_type(text, str):
            return False
        text = text.strip()
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"  # dingbats
            "\U000024c2-\U0001f251"  # enclosed characters
            "\U0001f900-\U0001f9ff"  # supplemental symbols and pictographs
            "\U0001fa70-\U0001faff"  # symbols and pictographs extended-A
            "\U00002600-\U000026ff"  # miscellaneous symbols
            "\U00002700-\U000027bf"  # dingbats
            "\U0001f004"  # mahjong tile red dragon
            "\U0001f0cf"  # playing card black joker
            "\U0001f18e"  # negative squared ab
            "\U0001f191-\U0001f19a"  # squared symbols
            "\U0001f201-\U0001f202"  # squared katakana
            "\U0001f21a-\U0001f22f"  # squared cjk ideographs
            "\U0001f232-\U0001f23a"  # squared cjk ideographs
            "\U0001f250-\U0001f251"  # circled ideographs
            "\U0000200d"  # zero width joiner
            "\U0000fe0f"  # variation selector-16
            "]+",
            flags=re.UNICODE,
        )

        return emoji_pattern.fullmatch(text) is not None

    def emojifie(self, text: str) -> str:
        tokens = text.split()
        for index, token in enumerate(tokens):
            for emoji in self.emojis:
                if token.lower() in emoji.name.lower():
                    tokens[index] = emoji.emoji
                    break
        return " ".join(tokens)

    def to_html(self, emoji: str) -> str:
        codepoints = [f"&#x{ord(char):X};" for char in emoji]
        return "".join(codepoints)
