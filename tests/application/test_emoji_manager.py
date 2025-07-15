from src.pymojis.application.pymojis_manager import PymojisManager


def test_get_all(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_all_emojis()
    assert len(emojis) > 0


def test_get_all_complex_emojis(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_all_emojis(exclude="complex")
    assert len(emojis[0].code) == 1


def test_get_random_emojis(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_random(length=10)
    assert len(emojis) == 10
    assert isinstance(emojis, list)


def test_get_emoji_by_code(pymoji_manager: PymojisManager):
    emoji = pymoji_manager.get_by_code("1F604")
    assert emoji == "😄"


def test_get_emoji_by_name(pymoji_manager: PymojisManager):
    emoji = pymoji_manager.get_by_name("grinning face with smiling eyes")
    assert emoji == "😄"


def test_get_emoji_by_category(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_by_category("Activities")
    assert len(emojis) > 0
