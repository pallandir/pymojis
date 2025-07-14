from src.domain.entities.emojis import Emoji


def test_emoji_repository_get_all(repository):
    result = repository.get_all(None)
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_by_code(repository):
    result = repository.get_by_code("1F600")
    assert result == "😀"


def test_emoji_repository_get_by_name(repository):
    result = repository.get_by_name("grinning face")
    assert result == "😀"


def test_emoji_repository_bet_by_category(repository):
    result = repository.get_by_category("Smileys & Emotion")
    assert isinstance(result, list)
    assert len(result) > 0
