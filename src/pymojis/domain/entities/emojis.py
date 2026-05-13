from typing import Any, Literal, Self, get_args
from uuid import uuid4

Categories = Literal[
    "Smileys & Emotion",
    "People & Body",
    "Animals & Nature",
    "Food & Drink",
    "Activities",
    "Travel & Places",
    "Objects",
    "Symbols",
    "Flags",
    "Component",
]

Qualification = Literal[
    "fully-qualified",
    "minimally-qualified",
    "unqualified",
    "component",
]


class Emoji:
    def __new__(
        cls,
        category: Categories,
        sub_category: str,
        code: list[str],
        name: str,
        emoji: str,
        unicode_version: str,
        qualification: Qualification,
        base_code: list[str] | None = None,
        keywords: list[str] | None = None,
        shortcodes: dict[str, str] | None = None,
    ) -> Self:
        valid_categories = get_args(Categories)
        valid_qualifications = get_args(Qualification)

        if not isinstance(category, str) or category not in valid_categories:
            valid_cats = ", ".join(f"'{cat}'" for cat in sorted(valid_categories))
            raise ValueError(f"category must be one of: {valid_cats}, got {category!r}")
        if not isinstance(sub_category, str) or not sub_category.strip():
            raise ValueError("Sub category should be a valid non-empty string")
        if (
            not isinstance(code, list)
            or not code
            or not all(isinstance(c, str) and c.strip() for c in code)
        ):
            raise ValueError("code must be a non-empty list of non-empty strings")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(emoji, str) or not emoji:
            raise ValueError("emoji must be a non-empty string")
        if not isinstance(unicode_version, str) or not unicode_version.strip():
            raise ValueError("unicode_version must be a non-empty string")
        if qualification not in valid_qualifications:
            valid_quals = ", ".join(f"'{q}'" for q in valid_qualifications)
            raise ValueError(
                f"qualification must be one of: {valid_quals}, got {qualification!r}"
            )
        if base_code is not None and (
            not isinstance(base_code, list)
            or not base_code
            or not all(isinstance(c, str) and c.strip() for c in base_code)
        ):
            raise ValueError("base_code must be None or a non-empty list of strings")
        if keywords is not None and (
            not isinstance(keywords, list)
            or not all(isinstance(k, str) for k in keywords)
        ):
            raise ValueError("keywords must be None or a list of strings")
        if shortcodes is not None and (
            not isinstance(shortcodes, dict)
            or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in shortcodes.items()
            )
        ):
            raise ValueError("shortcodes must be None or a dict of str→str")

        return super().__new__(cls)

    def __init__(
        self,
        category: str,
        sub_category: str,
        code: list[str],
        name: str,
        emoji: str,
        unicode_version: str,
        qualification: Qualification,
        base_code: list[str] | None = None,
        keywords: list[str] | None = None,
        shortcodes: dict[str, str] | None = None,
    ):
        self.id = str(uuid4())
        self.category = category
        self.sub_category = sub_category
        self.code = code
        self.name = name
        self.emoji = emoji
        self.unicode_version = unicode_version
        self.qualification: Qualification = qualification
        self.base_code = base_code
        self.keywords: list[str] = list(keywords) if keywords else []
        self.shortcodes: dict[str, str] = dict(shortcodes) if shortcodes else {}

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Emoji):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Emoji(name={self.name!r}, emoji={self.emoji!r}, code={self.code!r}, "
            f"category={self.category!r}, sub_category={self.sub_category!r}, "
            f"unicode_version={self.unicode_version!r}, qualification={self.qualification!r})"
        )
