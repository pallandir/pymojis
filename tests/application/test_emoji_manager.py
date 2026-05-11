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
