from typing import Literal

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
    def __init__(self, category: str, code: list[str], name: str, emoji: str) -> None:
        self.category = category
        self.code = code
        self.name = name
        self.emoji = emoji
