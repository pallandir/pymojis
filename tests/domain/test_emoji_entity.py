import pytest

from pymojis.domain.entities.emojis import Emoji


def test_create_emoji() -> None:
    emoji = Emoji(
        emoji="😄",
        code=["1F600"],
        name="grinning face",
        category="Smileys & Emotion",
        sub_category="faces",
        unicode_version="1.0",
        qualification="fully-qualified",
    )
    assert emoji.code == ["1F600"]
    assert emoji.name == "grinning face"
    assert emoji.category == "Smileys & Emotion"
    assert emoji.sub_category == "faces"
    assert emoji.unicode_version == "1.0"
    assert emoji.qualification == "fully-qualified"
    assert emoji.base_code is None
    assert emoji.keywords == []
    assert emoji.shortcodes == {}


def test_create_emoji_with_all_fields() -> None:
    emoji = Emoji(
        emoji="👍🏽",
        code=["1F44D", "1F3FD"],
        name="thumbs up: medium skin tone",
        category="People & Body",
        sub_category="hand-fingers-closed",
        unicode_version="1.0",
        qualification="fully-qualified",
        base_code=["1F44D"],
        keywords=["thumbs", "up", "hand"],
        shortcodes={"github": ":thumbs_up_medium_skin_tone:"},
    )
    assert emoji.base_code == ["1F44D"]
    assert emoji.keywords == ["thumbs", "up", "hand"]
    assert emoji.shortcodes == {"github": ":thumbs_up_medium_skin_tone:"}


def test_create_emoji_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        Emoji(
            emoji=123,  # type: ignore[arg-type]
            code=["1f600"],
            name="test",
            category=["test"],  # type: ignore[arg-type]
            sub_category=12345,  # type: ignore[arg-type]
            unicode_version="1.0",
            qualification="fully-qualified",
        )


def test_create_emoji_invalid_qualification_raises() -> None:
    with pytest.raises(ValueError, match="qualification"):
        Emoji(
            emoji="😄",
            code=["1F600"],
            name="grinning face",
            category="Smileys & Emotion",
            sub_category="faces",
            unicode_version="1.0",
            qualification="bogus",  # type: ignore[arg-type]
        )


def test_create_emoji_empty_unicode_version_raises() -> None:
    with pytest.raises(ValueError, match="unicode_version"):
        Emoji(
            emoji="😄",
            code=["1F600"],
            name="grinning face",
            category="Smileys & Emotion",
            sub_category="faces",
            unicode_version="",
            qualification="fully-qualified",
        )
