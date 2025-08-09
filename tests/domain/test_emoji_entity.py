import pytest

from src.pymojis.domain.entities.emojis import Emoji


def test_create_emoji():
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


def test_create_emoji_wrong():
    with pytest.raises(ValueError) as value_error:
        Emoji(
            emoji=123,
            code=["1f600"],
            name="test",
            category=["test"],
            sub_category=12345,
        )
    assert value_error
