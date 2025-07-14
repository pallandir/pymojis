from src.domain.entities.emojis import Emoji
from src.infrastructure.emojis_repository import EmojisRepository


def test_emoji_repository_get_all(repository: EmojisRepository):
    result = repository.get_all(None)
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_by_code(repository: EmojisRepository):
    result = repository.get_by_code("1F600")
    assert result == "😀"


def test_emoji_repository_get_by_name(repository: EmojisRepository):
    result = repository.get_by_name("grinning face")
    assert result == "😀"


def test_emoji_repository_bet_by_category(repository: EmojisRepository):
    result = repository.get_by_category("Smileys & Emotion")
    assert isinstance(result, list)
    assert len(result) > 0


def test_emoji_repository_get_random(repository: EmojisRepository):
    result = repository.get_random_emojis()
    assert isinstance(result[0], Emoji)
