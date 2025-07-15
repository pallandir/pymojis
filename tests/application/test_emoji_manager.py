from src.application.pymojis_manager import PymojisManager


def test_get_all(pymoji_manager: PymojisManager):
    emoji = pymoji_manager.get_all_emojis()
    assert len(emoji) > 0


def test_get_all_complex_emojis(pymoji_manager: PymojisManager):
    emoji = pymoji_manager.get_all_emojis(exclude="complex")
    assert len(emoji[0].code) == 1
