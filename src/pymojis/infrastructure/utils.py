from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji


def should_exclude(
    emoji: Emoji, exclude: Literal["complex"] | list[Categories]
) -> bool:
    if exclude == "complex":
        return len(emoji.code) > 1
    return emoji.category.lower() in {c.lower() for c in exclude}
