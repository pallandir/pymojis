from pymojis.domain.entities.emojis import Categories, Emoji
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
    result = repository.get_random_emojis(length=10, exclude="complex")
    assert all(len(emoji.code) == 1 for emoji in result)


def test_emoji_repository_get_random_large_length(repository: PymojisRepositoryImpl):
    result = repository.get_random_emojis(length=100000)
    assert len(result) == len(repository.get_all())


def test_emoji_repository_get_random_exclude_category(
    repository: PymojisRepositoryImpl,
):
    excluded_categories: list[Categories] = ["Smileys & Emotion"]
    result = repository.get_random_emojis(exclude=excluded_categories)
    assert all(emoji.category not in excluded_categories for emoji in result)


def test_emoji_repository_get_random_include_exclude(repository: PymojisRepositoryImpl):
    excluded_categories: list[Categories] = ["Smileys & Emotion"]
    result = repository.get_random_emojis(
        categories=excluded_categories, exclude=excluded_categories, length=10
    )
    assert all(emoji.category in excluded_categories for emoji in result)


def test_get_by_emoji(repository: PymojisRepositoryImpl):
    result = repository.get_by_emoji("😀")
    assert isinstance(result, Emoji)
    assert "1F600" in result.code


def test_contains_emojis(repository: PymojisRepositoryImpl):
    result = repository.contains_emojis("This string contains emoji: 😵‍💫")
    assert result is True


def test_contain_emojis_false(repository: PymojisRepositoryImpl):
    result = repository.contains_emojis("This string does not contain emojis")
    assert result is False


def test_is_emoji(repository: PymojisRepositoryImpl):
    assert repository.is_emoji("😵‍💫")
    assert repository.is_emoji(" 😵‍💫")


def test_is_emoji_false(repository: PymojisRepositoryImpl):
    assert not repository.is_emoji("")
    assert not repository.is_emoji("test 😵‍💫")


def test_emojifie(repository: PymojisRepositoryImpl):
    result = repository.emojifie("I'm sleepy")
    assert result == "I'm 😪"


def test_to_html(repository: PymojisRepositoryImpl):
    result = repository.to_html("😪")
    assert result == "&#x1F62A;"


def test_to_html_complex(repository: PymojisRepositoryImpl):
    result = repository.to_html("😵‍💫")
    assert result == "&#x1F635;&#x200D;&#x1F4AB;"
