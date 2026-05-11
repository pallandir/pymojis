import logging
import re
from random import sample
from typing import Any, Literal

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.domain.repositories.repository import PymojisRepository
from pymojis.infrastructure.data_loader.emojis_loader import (
    DatasetKind,
    EmojiDataLoader,
)
from pymojis.infrastructure.data_loader.file_loader import FileLoader

from .utils import should_exclude

_TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)


class PymojisRepositoryImpl(PymojisRepository):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._emojis: list[Emoji] = []
        self._emoji_chars: frozenset[str] = frozenset()
        self._name_index: dict[str, str] = {}
        self._token_index: dict[str, str] = {}
        self._data_loader = EmojiDataLoader(file_loader=FileLoader())

    def load_emojis(
        self, *, kind: DatasetKind = "light", path: str | None = None
    ) -> None:
        if path is not None:
            raw = self._data_loader.load_from_path(path)
        else:
            raw = self._data_loader.load(kind)
        self._parse_emojis(raw)
        self._emoji_chars = frozenset(e.emoji for e in self._emojis)
        self._name_index = {e.name.lower(): e.emoji for e in self._emojis}
        # Index emoji names by their lowercased word tokens. Skip 1- and
        # 2-letter tokens to avoid letter-buttons hijacking common pronouns
        # ("m" → Ⓜ, "i" → ℹ, etc.).
        token_index: dict[str, str] = {}
        for e in self._emojis:
            for token in e.name.lower().split():
                if len(token) < 3:
                    continue
                token_index.setdefault(token, e.emoji)
        self._token_index = token_index
        self.logger.info("Loaded %d emojis", len(self._emojis))

    def _parse_emojis(self, data: dict[str, Any]) -> None:
        emojis_data = data["emojis"]
        if not isinstance(emojis_data, dict):
            raise ValueError("Invalid data structure: 'emojis' must be a dictionary")

        parsed: list[Emoji] = []
        for category, subcategories in emojis_data.items():
            if not isinstance(subcategories, dict):
                raise ValueError(f"Invalid category '{category}': expected dict")
            for subcategory, emojis_list in subcategories.items():
                if not isinstance(emojis_list, list):
                    raise ValueError(
                        f"Invalid subcategory '{subcategory}': expected list"
                    )
                for emoji_data in emojis_list:
                    parsed.append(
                        self._create_emoji_from_data(category, subcategory, emoji_data)
                    )
        self._emojis = parsed

    @staticmethod
    def _create_emoji_from_data(
        category: Categories, subcategory: str, emoji_data: dict[str, Any]
    ) -> Emoji:
        if not isinstance(emoji_data, dict):
            raise TypeError("Emoji entry must be a dictionary")
        return Emoji(
            category=category,
            sub_category=subcategory,
            name=emoji_data["name"],
            code=emoji_data["code"],
            emoji=emoji_data["emoji"],
        )

    def get_all(
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]:
        if exclude is None:
            return self._emojis.copy()
        return [e for e in self._emojis if not should_exclude(e, exclude)]

    def get_by_category(self, category: Categories) -> list[str]:
        if not isinstance(category, str):
            raise TypeError(f"category must be str, got {type(category).__name__}")
        target = category.lower()
        return [e.emoji for e in self._emojis if e.category.lower() == target]

    def get_by_code(self, code: str) -> str | None:
        if not isinstance(code, str):
            raise TypeError(f"code must be str, got {type(code).__name__}")
        target = code.lower()
        for e in self._emojis:
            if len(e.code) == 1 and e.code[0].lower() == target:
                return e.emoji
        return None

    def get_by_name(self, name: str) -> str | None:
        if not isinstance(name, str):
            raise TypeError(f"name must be str, got {type(name).__name__}")
        return self._name_index.get(name.lower())

    def get_random_emojis(
        self,
        categories: list[Categories] | None = None,
        length: int = 1,
        exclude: Literal["complex"] | list[Categories] | None = None,
    ) -> list[Emoji]:
        if length < 0:
            raise ValueError(f"length must be >= 0, got {length}")
        if categories:
            wanted = {c.lower() for c in categories}
            pool = [e for e in self._emojis if e.category.lower() in wanted]
        elif exclude is not None:
            pool = [e for e in self._emojis if not should_exclude(e, exclude)]
        else:
            pool = self._emojis
        return sample(pool, min(length, len(pool)))

    def get_by_emoji(self, emoji: str) -> Emoji | None:
        for e in self._emojis:
            if e.emoji == emoji:
                return e
        return None

    def contains_emojis(self, text: str) -> bool:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        # Fast path: any single-codepoint emoji char present?
        if any(ch in self._emoji_chars for ch in text):
            return True
        # Slow path: multi-codepoint emoji (ZWJ sequences, flags, etc.)
        return any(e.emoji in text for e in self._emojis if len(e.emoji) > 1)

    def is_emoji(self, text: str) -> bool:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        return text.strip() in self._emoji_chars

    def emojifie(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")

        def replace(match: re.Match[str]) -> str:
            emoji = self._token_index.get(match.group(0).lower())
            return emoji if emoji is not None else match.group(0)

        return _TOKEN_RE.sub(replace, text)

    def to_html(self, emoji: str) -> str:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        return "".join(f"&#x{ord(ch):X};" for ch in emoji)
