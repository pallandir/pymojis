from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji


def should_exclude(emoji: Emoji, exclude: Literal["complex"] | list[Categories] | None):
    if exclude == "complex" and len(emoji.code) > 1:
        return True
    if isinstance(exclude, list) and emoji.category.lower() in (
        excluded.lower() for excluded in exclude
    ):
        return True
    return False
