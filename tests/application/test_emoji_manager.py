import pytest

from pymojis import Categories, Emoji, PymojisManager
from pymojis.infrastructure.exceptions import DatasetNotFoundError


def test_categories_is_re_exported() -> None:
    # Categories is a Literal alias; importing it from the package root must work.
    assert Categories is not None


def test_get_all(manager: PymojisManager) -> None:
    emojis = manager.get_all_emojis()
    assert len(emojis) > 0


def test_get_all_exclude_complex(manager: PymojisManager) -> None:
    emojis = manager.get_all_emojis(exclude="complex")
    assert all(len(emoji.code) == 1 for emoji in emojis)


def test_get_random_emojis(manager: PymojisManager) -> None:
    emojis = manager.get_random(length=10)
    assert len(emojis) == 10
    assert isinstance(emojis[0], Emoji)
    assert isinstance(emojis, list)


def test_get_emoji_by_code(manager: PymojisManager) -> None:
    assert manager.get_by_code("1F604") == "😄"


def test_get_emoji_by_code_lower(manager: PymojisManager) -> None:
    assert manager.get_by_code("1f604") == "😄"


def test_get_emoji_by_code_wrong_type(manager: PymojisManager) -> None:
    with pytest.raises(TypeError):
        manager.get_by_code(1234)  # type: ignore[arg-type]


def test_get_emoji_by_name(manager: PymojisManager) -> None:
    assert manager.get_by_name("grinning face with smiling eyes") == "😄"


def test_get_emoji_by_name_wrong_type(manager: PymojisManager) -> None:
    with pytest.raises(TypeError):
        manager.get_by_name(1234)  # type: ignore[arg-type]


def test_get_emoji_by_category(manager: PymojisManager) -> None:
    emojis = manager.get_by_category("Activities")
    assert len(emojis) > 0
    assert all(isinstance(emoji, str) for emoji in emojis)


def test_use_full_dataset_loads_when_available() -> None:
    pytest.importorskip("pymojis_fulldata")
    manager = PymojisManager(use_full_dataset=True)
    assert len(manager.get_all_emojis()) > 0


def test_use_full_dataset_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "pymojis_fulldata", None)
    monkeypatch.setitem(sys.modules, "pymojis_fulldata.data", None)
    with pytest.raises(DatasetNotFoundError):
        PymojisManager(use_full_dataset=True)


def test_extract_facade(manager: PymojisManager) -> None:
    result = manager.extract("hi 😀")
    assert len(result) == 1
    assert result[0].emoji == "😀"


def test_find_facade(manager: PymojisManager) -> None:
    matches = list(manager.find("😀 here"))
    assert len(matches) == 1
    _, start, end = matches[0]
    assert start == 0
    assert end == len("😀")


def test_count_facade(manager: PymojisManager) -> None:
    assert manager.count("😀😀") == 2


def test_count_by_facade(manager: PymojisManager) -> None:
    counts = manager.count_by("😀 hi 😀")
    assert sum(counts.values()) == 2


def test_strip_facade(manager: PymojisManager) -> None:
    assert manager.strip("a 😀 b") == "a  b"  # noqa: B005


def test_replace_facade_literal(manager: PymojisManager) -> None:
    assert manager.replace("hi 😀", "X") == "hi X"


def test_replace_facade_callable(manager: PymojisManager) -> None:
    assert manager.replace("hi 😀", lambda e: e.name.upper()) == "hi GRINNING FACE"


def test_demojifie_facade(manager: PymojisManager) -> None:
    assert manager.demojifie("hi 😀") == "hi :grinning_face:"


def test_to_codepoint_string_facade(manager: PymojisManager) -> None:
    assert manager.to_codepoint_string("😀") == "U+1F600"


def test_to_unicode_escape_facade(manager: PymojisManager) -> None:
    assert manager.to_unicode_escape("😀") == r"\U0001F600"


def test_to_image_url_facade(manager: PymojisManager) -> None:
    assert manager.to_image_url("😀").endswith("/1f600.svg")


def test_flag_for_facade(manager: PymojisManager) -> None:
    assert manager.flag_for("FR") == "\U0001f1eb\U0001f1f7"


def test_country_of_facade(manager: PymojisManager) -> None:
    assert manager.country_of("\U0001f1eb\U0001f1f7") == "FR"


def test_is_flag_facade(manager: PymojisManager) -> None:
    assert manager.is_flag("\U0001f1eb\U0001f1f7")
    assert not manager.is_flag("😀")


def test_shortcode_full_roundtrip() -> None:
    pytest.importorskip("pymojis_fulldata")
    full = PymojisManager(use_full_dataset=True)
    code = full.to_shortcode("😀")
    assert code is not None
    assert full.from_shortcode(code) == "😀"
