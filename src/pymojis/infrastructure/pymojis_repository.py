import logging
import re
from random import sample
from typing import Any, Literal

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.domain.repositories.repository import PymojisRepository
from pymojis.infrastructure.data_loader.emojis_loader import EmojiDataLoader
from pymojis.infrastructure.data_loader.file_loader import FileLoader

from .exceptions import InfrastructureError
from .utils import check_type, should_exclude


class PymojisRepositoryImpl(PymojisRepository):
    def __init__(self, data_file_path: str | None = None):
        self.data_file_path: str | None = data_file_path
        self.logger = logging.getLogger(__name__)
        self._emojis: list[Emoji] = []
        self._data_loader: EmojiDataLoader = EmojiDataLoader(file_loader=FileLoader())

    def load_emojis(self, data_file_path: str | None = None) -> None:
        try:
            if data_file_path:
                self.logger.info(f"Loading emojis from custom path: {data_file_path}")
                raw_data = self._data_loader.load_from_path(data_file_path)
            else:
                self.logger.info("Loading emojis from default sources")
                raw_data = self._data_loader.load_from_default_sources()

            self._parse_emojis(raw_data)
            self.logger.info(f"Successfully loaded {len(self._emojis)} emojis")

        except Exception as infra_error:
            self.logger.error(f"Failed to load emojis: {infra_error}")
            raise InfrastructureError(
                f"Emoji loading failed: {infra_error}"
            ) from infra_error

    def _parse_emojis(self, data: dict[str, Any]) -> None:
        try:
            emojis_data = data.get("emojis", {})
            if not isinstance(emojis_data, dict):
                raise InfrastructureError(
                    "Invalid data structure: 'emojis' must be a dictionary"
                )

            parsed_emojis = []

            for category, subcategories in emojis_data.items():
                if not isinstance(subcategories, dict):
                    self.logger.warning(f"Skipping invalid category '{category}'")
                    continue

                for subcategory, emojis_list in subcategories.items():
                    if not isinstance(emojis_list, list):
                        self.logger.warning(
                            f"Skipping invalid subcategory '{subcategory}'"
                        )
                        continue

                    for emoji_data in emojis_list:
                        try:
                            emoji = self._create_emoji_from_data(
                                category, subcategory, emoji_data
                            )
                            parsed_emojis.append(emoji)
                        except Exception as invalid_emoji:
                            self.logger.warning(
                                f"Skipping invalid emoji: {invalid_emoji}"
                            )
                            continue

            self._emojis = parsed_emojis
            self.logger.debug(f"Parsed {len(self._emojis)} emojis successfully")

        except Exception as infra_error:
            raise InfrastructureError(
                f"Failed to parse emoji data: {infra_error}"
            ) from infra_error

    def _create_emoji_from_data(
        self, category: Categories, subcategory: str, emoji_data: dict[str, Any]
    ) -> Emoji:
        if not isinstance(emoji_data, dict):
            raise ValueError("Emoji data must be a dictionary")

        return Emoji(
            category=category,
            sub_category=subcategory,
            name=emoji_data.get("name", ""),
            code=emoji_data.get("code", ""),
            emoji=emoji_data.get("emoji", ""),
        )

    def get_all(
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]:
        all_emojis: list[Emoji] = []
        if not exclude:
            all_emojis = self._emojis.copy()
        else:
            for emoji in self._emojis:
                if should_exclude(emoji, exclude):
                    continue
                all_emojis.append(emoji)
        return all_emojis

    def get_by_category(self, category: Categories) -> list[str]:
        if not check_type(category, str):
            return []
        return [
            emoji.emoji
            for emoji in self._emojis
            if category.lower() == emoji.category.lower()
        ]

    def get_by_code(self, code: str) -> str | None:
        if not check_type(code, str):
            return None
        return next(
            (
                emoji.emoji
                for emoji in self._emojis
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
                for emoji in self._emojis
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
        if categories:
            category_set = {cat.lower() for cat in categories}
            filtered = [
                emoji
                for emoji in self._emojis
                if emoji.category.lower() in category_set
            ]
        else:
            filtered = (
                [emoji for emoji in self._emojis if not should_exclude(emoji, exclude)]
                if exclude
                else self._emojis.copy()
            )

        return sample(filtered, min(length, len(filtered)))

    def get_by_emoji(self, emoji: str) -> Emoji | None:
        found_emoji = None
        for current_emoji in self._emojis:
            if current_emoji.emoji == emoji:
                found_emoji = current_emoji
                break

        return found_emoji

    def contains_emojis(self, text: str) -> bool:
        for emoji in self._emojis:
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
            for emoji in self._emojis:
                if token.lower() in emoji.name.lower():
                    tokens[index] = emoji.emoji
                    break
        return " ".join(tokens)

    def to_html(self, emoji: str) -> str:
        codepoints = [f"&#x{ord(char):X};" for char in emoji]
        return "".join(codepoints)
