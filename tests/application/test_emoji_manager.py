from src.application.pymojis_manager import PymojisManager


def test_get_all(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_all_emojis()
    assert len(emojis) > 0


def test_get_all_complex_emojis(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_all_emojis(exclude="complex")
    assert len(emojis[0].code) == 1


def test_get_random_emojis(pymoji_manager: PymojisManager):
    emojis = pymoji_manager.get_random(length=10)
    assert len(emojis) == 10
