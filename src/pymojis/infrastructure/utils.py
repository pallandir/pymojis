import warnings
from typing import Any, Literal

from pymojis.domain.entities.emojis import Categories, Emoji


def should_exclude(emoji: Emoji, exclude: Literal["complex"] | list[Categories] | None):
    if exclude == "complex" and len(emoji.code) > 1:
        return True
    if isinstance(exclude, list) and emoji.category.lower() in (
        excluded.lower() for excluded in exclude
    ):
        return True
    return False


def check_type(value, expected_type: type[Any] | tuple[type[Any], ...]) -> bool:
    if not isinstance(value, expected_type):
        warnings.warn(
            f"\n\nExpected type {expected_type}, got {type(value)}\n", stacklevel=1
        )
        return False
    return True
