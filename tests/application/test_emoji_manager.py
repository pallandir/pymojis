from pymojis.domain.entities.emojis import Emoji
from src.pymojis.application.pymojis_manager import PymojisManager


def test_get_all(manager: PymojisManager):
    emojis = manager.get_all_emojis()
    assert len(emojis) > 0


def test_get_all_exclude_complex(manager: PymojisManager):
    emojis = manager.get_all_emojis(exclude="complex")
    assert all(len(emoji.code) == 1 for emoji in emojis)


def test_get_random_emojis(manager: PymojisManager):
    emojis = manager.get_random(length=10)
    assert len(emojis) == 10
    assert isinstance(emojis[0], Emoji)
    assert isinstance(emojis, list)


def test_get_emoji_by_code(manager: PymojisManager):
    emoji = manager.get_by_code("1F604")
    assert emoji == "😄"


def test_get_emoji_by_code_lower(manager: PymojisManager):
    emoji = manager.get_by_code("1f604")
    assert emoji == "😄"


def test_get_emoji_by_code_wrong_value(manager: PymojisManager):
    emoji = manager.get_by_code(1234)
    assert emoji is None


def test_get_emoji_by_name(manager: PymojisManager):
    emoji = manager.get_by_name("grinning face with smiling eyes")
    assert emoji == "😄"


def test_get_emoji_by_name_wrong_value(manager: PymojisManager):
    emoji = manager.get_by_name(1234)
    assert emoji is None


def test_get_emoji_by_category(manager: PymojisManager):
    emojis = manager.get_by_category("Activities")
    assert len(emojis) > 0
    assert all(isinstance(emoji, str) for emoji in emojis)
