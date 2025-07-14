from src.domain.entities.emojis import Emoji


def test_emoji_repository_get_all(repository):
    result = repository.get_all(None)
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_by_code(repository):
    result = repository.get_by_code("1F600")
    # assert result == "😀"

    print("result::", result)
