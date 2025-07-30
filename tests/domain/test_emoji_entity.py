import pytest

from src.pymojis.domain.entities.emojis import Emoji


def test_create_emoji():
    emoji = Emoji(
        emoji="😄", code=["1F600"], name="grinning face", category="Smileys & Emotion"
    )
    assert emoji.code == ["1F600"]
    assert emoji.name == "grinning face"
    assert emoji.category == "Smileys & Emotion"


def test_create_emoji_wrong():
    with pytest.raises(ValueError) as value_error:
        Emoji(emoji=123, code=["1f600"], name="test", category=["test"])
    assert value_error
