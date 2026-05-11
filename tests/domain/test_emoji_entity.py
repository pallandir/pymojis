import pytest

from pymojis.domain.entities.emojis import Emoji


def test_create_emoji() -> None:
    emoji = Emoji(
        emoji="😄",
        code=["1F600"],
        name="grinning face",
        category="Smileys & Emotion",
        sub_category="faces",
    )
    assert emoji.code == ["1F600"]
    assert emoji.name == "grinning face"
    assert emoji.category == "Smileys & Emotion"
    assert emoji.sub_category == "faces"


def test_create_emoji_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        Emoji(
            emoji=123,  # type: ignore[arg-type]
            code=["1f600"],
            name="test",
            category=["test"],  # type: ignore[arg-type]
            sub_category=12345,  # type: ignore[arg-type]
        )
