from src.domain.entities.emojis import Emoji


def test_create_emoji():
    emoji = Emoji(
        emoji="😄", code=["1F600"], name="grinning face", category="Smiley & Emotions"
    )
    assert emoji.code == ["1F600"]
    assert emoji.name == "grinning face"
    assert emoji.category == "Smiley & Emotions"
