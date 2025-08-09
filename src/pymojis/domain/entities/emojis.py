from typing import Literal, get_args
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


class Emoji:
    def __new__(
        cls,
        category: Categories,
        sub_category: str,
        code: list[str],
        name: str,
        emoji: str,
    ):
        valid_categories = get_args(Categories)

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

        return super().__new__(cls)

    def __init__(
        self, category: str, sub_category: str, code: list[str], name: str, emoji: str
    ) -> None:
        self.id = str(uuid4())
        self.category = category
        self.sub_category = sub_category
        self.code = code
        self.name = name
        self.emoji = emoji

    def __eq__(self, other) -> bool:
        if not isinstance(other, Emoji):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Emoji(name={self.name!r}, emoji={self.emoji!r}, code={self.code!r}, category={self.category!r}, sub_category={self.sub_category!r})"
