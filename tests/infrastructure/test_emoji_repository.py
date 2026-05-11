import pytest

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


def test_emoji_repository_get_all(repository: PymojisRepositoryImpl) -> None:
    result = repository.get_all(None)
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_by_code(repository: PymojisRepositoryImpl) -> None:
    assert repository.get_by_code("1F600") == "😀"


def test_emoji_repository_get_by_name(repository: PymojisRepositoryImpl) -> None:
    assert repository.get_by_name("grinning face") == "😀"


def test_emoji_repository_get_by_category(repository: PymojisRepositoryImpl) -> None:
    result = repository.get_by_category("Smileys & Emotion")
    assert isinstance(result, list)
    assert len(result) > 0


def test_emoji_repository_get_random(repository: PymojisRepositoryImpl) -> None:
    result = repository.get_random_emojis()
    assert isinstance(result[0], Emoji)


def test_emoji_repository_get_random_exclude(repository: PymojisRepositoryImpl) -> None:
    result = repository.get_random_emojis(length=10, exclude="complex")
    assert all(len(emoji.code) == 1 for emoji in result)


def test_emoji_repository_get_random_large_length(
    repository: PymojisRepositoryImpl,
) -> None:
    result = repository.get_random_emojis(length=100000)
    assert len(result) == len(repository.get_all())


def test_emoji_repository_get_random_exclude_category(
    repository: PymojisRepositoryImpl,
) -> None:
    excluded: list[Categories] = ["Smileys & Emotion"]
    result = repository.get_random_emojis(exclude=excluded)
    assert all(emoji.category not in excluded for emoji in result)


def test_emoji_repository_get_random_categories_take_precedence(
    repository: PymojisRepositoryImpl,
) -> None:
    cats: list[Categories] = ["Smileys & Emotion"]
    result = repository.get_random_emojis(categories=cats, exclude=cats, length=10)
    assert all(emoji.category in cats for emoji in result)


def test_get_by_emoji(repository: PymojisRepositoryImpl) -> None:
    result = repository.get_by_emoji("😀")
    assert isinstance(result, Emoji)
    assert "1F600" in result.code


def test_contains_emojis(repository: PymojisRepositoryImpl) -> None:
    assert repository.contains_emojis("This string contains emoji: 😵‍💫") is True


def test_contain_emojis_false(repository: PymojisRepositoryImpl) -> None:
    assert repository.contains_emojis("This string does not contain emojis") is False


def test_is_emoji(repository: PymojisRepositoryImpl) -> None:
    assert repository.is_emoji("😵‍💫")
    assert repository.is_emoji(" 😵‍💫")


def test_is_emoji_false(repository: PymojisRepositoryImpl) -> None:
    assert not repository.is_emoji("")
    assert not repository.is_emoji("test 😵‍💫")


def test_emojifie(repository: PymojisRepositoryImpl) -> None:
    assert repository.emojifie("I'm sleepy") == "I'm 😪"


def test_emojifie_no_match_unchanged(repository: PymojisRepositoryImpl) -> None:
    assert repository.emojifie("zzzz xyzzy") == "zzzz xyzzy"


def test_emojifie_wrong_type_raises(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(TypeError):
        repository.emojifie(123)  # type: ignore[arg-type]


def test_to_html(repository: PymojisRepositoryImpl) -> None:
    assert repository.to_html("😪") == "&#x1F62A;"


def test_to_html_complex(repository: PymojisRepositoryImpl) -> None:
    assert repository.to_html("😵‍💫") == "&#x1F635;&#x200D;&#x1F4AB;"
