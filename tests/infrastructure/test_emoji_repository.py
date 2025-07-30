from pymojis.domain.entities.emojis import Emoji
from pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


def test_emoji_repository_get_all(repository: PymojisRepositoryImpl):
    result = repository.get_all(None)
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_by_code(repository: PymojisRepositoryImpl):
    result = repository.get_by_code("1F600")
    assert result == "😀"


def test_emoji_repository_get_by_name(repository: PymojisRepositoryImpl):
    result = repository.get_by_name("grinning face")
    assert result == "😀"


def test_emoji_repository_bet_by_category(repository: PymojisRepositoryImpl):
    result = repository.get_by_category("Smileys & Emotion")
    assert isinstance(result, list)
    assert len(result) > 0


def test_emoji_repository_get_random(repository: PymojisRepositoryImpl):
    result = repository.get_random_emojis()
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_random_exclude(repository: PymojisRepositoryImpl):
    result = repository.get_random_emojis(exclude="complex")
    assert all(len(emoji.code) == 1 for emoji in result)
