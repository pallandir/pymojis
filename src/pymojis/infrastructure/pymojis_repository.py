import logging
import re
from collections.abc import Callable, Iterator
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
_DEMOJI_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify_name(name: str) -> str:
    return _DEMOJI_SLUG_RE.sub("_", name.lower()).strip("_")


_RIS_FIRST = 0x1F1E6  # Regional Indicator Symbol A
_RIS_LAST = 0x1F1FF  # Regional Indicator Symbol Z
_VARIATION_SELECTOR_16 = "FE0F"


def _is_ris_pair(emoji: str) -> bool:
    if len(emoji) != 2:
        return False
    return all(_RIS_FIRST <= ord(c) <= _RIS_LAST for c in emoji)


class PymojisRepositoryImpl(PymojisRepository):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._emojis: list[Emoji] = []
        self._emoji_chars: frozenset[str] = frozenset()
        self._name_index: dict[str, str] = {}
        self._token_index: dict[str, str] = {}
        self._char_to_emoji: dict[str, Emoji] = {}
        self._emoji_pattern: re.Pattern[str] = re.compile("(?!x)x")
        self._code_to_emoji_str: dict[tuple[str, ...], str] = {}
        self._base_to_variants: dict[tuple[str, ...], list[str]] = {}
        self._shortcode_by_set: dict[tuple[str, str], str] = {}
        self._shortcode_any: dict[str, str] = {}
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
        # Longest-match-first alternation: Python's `re` tries alternatives
        # left to right, so ZWJ sequences and skin-tone composites must
        # appear before their bare base ("👍🏽" before "👍").
        sorted_emojis = sorted(self._emojis, key=lambda e: len(e.emoji), reverse=True)
        self._char_to_emoji = {e.emoji: e for e in sorted_emojis}
        self._emoji_pattern = re.compile(
            "|".join(re.escape(e.emoji) for e in sorted_emojis)
        )
        # Family / shortcode indices — empty for the light dataset, populated
        # for the full one. Callers see None / [] either way.
        self._code_to_emoji_str = {tuple(e.code): e.emoji for e in self._emojis}
        base_to_variants: dict[tuple[str, ...], list[str]] = {}
        for e in self._emojis:
            if e.base_code:
                base_to_variants.setdefault(tuple(e.base_code), []).append(e.emoji)
        self._base_to_variants = base_to_variants
        shortcode_by_set: dict[tuple[str, str], str] = {}
        shortcode_any: dict[str, str] = {}
        for e in self._emojis:
            for set_name, code in e.shortcodes.items():
                shortcode_by_set[(set_name, code)] = e.emoji
                shortcode_any.setdefault(code, e.emoji)
        self._shortcode_by_set = shortcode_by_set
        self._shortcode_any = shortcode_any
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
        required = ("name", "code", "emoji", "unicode_version", "qualification")
        missing = [k for k in required if k not in emoji_data]
        if missing:
            raise ValueError(
                f"Emoji record missing required fields {missing}: {emoji_data!r}"
            )
        return Emoji(
            category=category,
            sub_category=subcategory,
            name=emoji_data["name"],
            code=emoji_data["code"],
            emoji=emoji_data["emoji"],
            unicode_version=emoji_data["unicode_version"],
            qualification=emoji_data["qualification"],
            base_code=emoji_data.get("base_code"),
            keywords=emoji_data.get("keywords"),
            shortcodes=emoji_data.get("shortcodes"),
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
        return self._char_to_emoji.get(emoji)

    def contains_emojis(self, text: str) -> bool:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        return self._emoji_pattern.search(text) is not None

    def extract(self, text: str) -> list[Emoji]:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        return [e for e, _, _ in self._iter_emojis(text)]

    def find(self, text: str) -> Iterator[tuple[Emoji, int, int]]:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        return self._iter_emojis(text)

    def count(self, text: str) -> int:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        return sum(1 for _ in self._iter_emojis(text))

    def count_by(self, text: str) -> dict[Emoji, int]:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        counts: dict[Emoji, int] = {}
        for emoji, _, _ in self._iter_emojis(text):
            counts[emoji] = counts.get(emoji, 0) + 1
        return counts

    def strip(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        return self._emoji_pattern.sub("", text)

    def replace(self, text: str, repl: str | Callable[[Emoji], str]) -> str:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        if isinstance(repl, str):
            literal = repl
            return self._emoji_pattern.sub(lambda _m: literal, text)
        if not callable(repl):
            raise TypeError("repl must be str or callable")

        def _apply(match: re.Match[str]) -> str:
            return repl(self._char_to_emoji[match.group(0)])

        return self._emoji_pattern.sub(_apply, text)

    def demojifie(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")

        def _to_name(match: re.Match[str]) -> str:
            emoji = self._char_to_emoji[match.group(0)]
            return f":{_slugify_name(emoji.name)}:"

        return self._emoji_pattern.sub(_to_name, text)

    def _iter_emojis(self, text: str) -> Iterator[tuple[Emoji, int, int]]:
        for match in self._emoji_pattern.finditer(text):
            yield self._char_to_emoji[match.group(0)], match.start(), match.end()

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

    def to_codepoint_string(
        self, emoji: str, sep: str = " ", prefix: str = "U+"
    ) -> str:
        if not isinstance(emoji, str) or not emoji:
            raise ValueError(f"emoji must be a non-empty string, got {emoji!r}")
        return sep.join(f"{prefix}{ord(c):04X}" for c in emoji)

    def to_unicode_escape(self, emoji: str) -> str:
        if not isinstance(emoji, str) or not emoji:
            raise ValueError(f"emoji must be a non-empty string, got {emoji!r}")
        return "".join(f"\\U{ord(c):08X}" for c in emoji)

    def to_image_url(
        self,
        emoji: str,
        provider: Literal["twemoji", "openmoji"] = "twemoji",
        extension: Literal["svg", "png"] = "svg",
    ) -> str:
        if not isinstance(emoji, str) or not emoji:
            raise ValueError(f"emoji must be a non-empty string, got {emoji!r}")
        cps = [f"{ord(c):X}" for c in emoji]
        if provider == "twemoji":
            seq = "-".join(cp.lower() for cp in cps)
            return (
                "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/"
                f"{extension}/{seq}.{extension}"
            )
        if provider == "openmoji":
            stripped = [cp for cp in cps if cp != _VARIATION_SELECTOR_16]
            if not stripped:
                raise ValueError(
                    f"emoji has no displayable codepoints after stripping VS16: {emoji!r}"
                )
            seq = "-".join(stripped)
            return f"https://openmoji.org/data/color/{extension}/{seq}.{extension}"
        raise ValueError(f"unknown provider: {provider!r}")

    def to_shortcode(self, emoji: str, set_name: str = "github") -> str | None:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        if not isinstance(set_name, str) or not set_name:
            raise ValueError("set_name must be a non-empty string")
        record = self._char_to_emoji.get(emoji)
        if record is None:
            return None
        return record.shortcodes.get(set_name)

    def from_shortcode(self, code: str, set_name: str | None = None) -> str | None:
        if not isinstance(code, str):
            raise TypeError(f"code must be str, got {type(code).__name__}")
        if set_name is not None:
            if not isinstance(set_name, str) or not set_name:
                raise ValueError("set_name must be None or a non-empty string")
            return self._shortcode_by_set.get((set_name, code))
        return self._shortcode_any.get(code)

    def base_of(self, emoji: str) -> str | None:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        record = self._char_to_emoji.get(emoji)
        if record is None or not record.base_code:
            return None
        return self._code_to_emoji_str.get(tuple(record.base_code))

    def skin_tones(self, emoji: str) -> list[str]:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        record = self._char_to_emoji.get(emoji)
        if record is None:
            return []
        # If `emoji` is itself a variant, return siblings under the same base.
        key = tuple(record.base_code) if record.base_code else tuple(record.code)
        return list(self._base_to_variants.get(key, []))

    def is_flag(self, emoji: str) -> bool:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        # Two paths: a known record in the Flags category, OR a bare 2-letter
        # RIS sequence that isn't in the dataset yet (rare but valid Unicode).
        record = self._char_to_emoji.get(emoji)
        if record is not None:
            return record.category == "Flags"
        return _is_ris_pair(emoji)

    def flag_for(self, country_code: str) -> str:
        if not isinstance(country_code, str):
            raise TypeError(
                f"country_code must be str, got {type(country_code).__name__}"
            )
        if len(country_code) != 2 or not country_code.isalpha():
            raise ValueError(
                f"country_code must be 2 ASCII letters (ISO 3166-1 alpha-2), "
                f"got {country_code!r}"
            )
        cc = country_code.upper()
        return "".join(chr(_RIS_FIRST + ord(c) - ord("A")) for c in cc)

    def country_of(self, emoji: str) -> str | None:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        if not _is_ris_pair(emoji):
            return None
        return "".join(chr(ord("A") + ord(c) - _RIS_FIRST) for c in emoji)

    def search(self, query: str, limit: int = 10) -> list[Emoji]:
        if not isinstance(query, str):
            raise TypeError(f"query must be str, got {type(query).__name__}")
        if limit < 0:
            raise ValueError(f"limit must be >= 0, got {limit}")
        q = query.strip().lower()
        if not q:
            return []
        scored: list[tuple[int, str, str, Emoji]] = []
        for e in self._emojis:
            score = 0
            name_low = e.name.lower()
            if name_low == q:
                score = 100
            elif q in name_low:
                score = 50
            elif any(q == t for t in name_low.split()):
                score = 40
            for kw in e.keywords:
                kw_low = kw.lower()
                if kw_low == q:
                    score = max(score, 30)
                elif q in kw_low:
                    score = max(score, 15)
            if score:
                scored.append((-score, e.name, e.emoji, e))
        scored.sort()
        return [e for _, _, _, e in scored[:limit]]

    def suggest(self, emoji: str, limit: int = 5) -> list[Emoji]:
        if not isinstance(emoji, str):
            raise TypeError(f"emoji must be str, got {type(emoji).__name__}")
        if limit < 0:
            raise ValueError(f"limit must be >= 0, got {limit}")
        source = self._char_to_emoji.get(emoji)
        if source is None:
            return []
        source_kws = {kw.lower() for kw in source.keywords}
        scored: list[tuple[int, str, str, Emoji]] = []
        for e in self._emojis:
            if e.emoji == emoji:
                continue
            score = 0
            if e.sub_category == source.sub_category:
                score += 10
            elif e.category == source.category:
                score += 2
            if source_kws:
                shared = source_kws & {kw.lower() for kw in e.keywords}
                score += 5 * len(shared)
            if score:
                scored.append((-score, e.name, e.emoji, e))
        scored.sort()
        return [e for _, _, _, e in scored[:limit]]

    def categories(self) -> list[str]:
        seen: dict[str, None] = {}
        for e in self._emojis:
            seen.setdefault(e.category, None)
        return list(seen)

    def sub_categories(self, category: str | None = None) -> list[str]:
        if category is not None and not isinstance(category, str):
            raise TypeError(
                f"category must be str or None, got {type(category).__name__}"
            )
        if category is not None:
            target = category.lower()
            pool = (e for e in self._emojis if e.category.lower() == target)
        else:
            pool = (e for e in self._emojis)
        seen: dict[str, None] = {}
        for e in pool:
            seen.setdefault(e.sub_category, None)
        return list(seen)

    def get_by_subcategory(self, name: str) -> list[Emoji]:
        if not isinstance(name, str):
            raise TypeError(f"name must be str, got {type(name).__name__}")
        target = name.lower()
        return [e for e in self._emojis if e.sub_category.lower() == target]
