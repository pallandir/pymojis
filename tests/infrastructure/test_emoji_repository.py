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


def test_extract_returns_emojis_in_order(repository: PymojisRepositoryImpl) -> None:
    result = repository.extract("hello 😀 and 😪 again 😀")
    assert [e.emoji for e in result] == ["😀", "😪", "😀"]


def test_extract_empty_text(repository: PymojisRepositoryImpl) -> None:
    assert repository.extract("no emojis here") == []


def test_extract_zwj_sequence_matches_whole(repository: PymojisRepositoryImpl) -> None:
    # 😵‍💫 is U+1F635 ZWJ U+1F4AB — must match as one unit, not three pieces.
    result = repository.extract("dizzy 😵‍💫 day")
    assert len(result) == 1
    assert result[0].emoji == "😵‍💫"


def test_find_returns_positions(repository: PymojisRepositoryImpl) -> None:
    text = "a 😀 b"
    matches = list(repository.find(text))
    assert len(matches) == 1
    emoji, start, end = matches[0]
    assert emoji.emoji == "😀"
    assert text[start:end] == "😀"


def test_count(repository: PymojisRepositoryImpl) -> None:
    assert repository.count("😀😀😪") == 3
    assert repository.count("no emojis") == 0


def test_count_by(repository: PymojisRepositoryImpl) -> None:
    result = repository.count_by("😀 hi 😀 there 😪")
    by_char = {e.emoji: c for e, c in result.items()}
    assert by_char == {"😀": 2, "😪": 1}


def test_strip(repository: PymojisRepositoryImpl) -> None:
    assert repository.strip("hello 😀 world 😪!") == "hello  world !"  # noqa: B005


def test_strip_no_emojis_returns_input(repository: PymojisRepositoryImpl) -> None:
    assert repository.strip("plain text") == "plain text"  # noqa: B005


def test_replace_with_literal(repository: PymojisRepositoryImpl) -> None:
    assert repository.replace("hi 😀 there 😪", "[e]") == "hi [e] there [e]"


def test_replace_with_callable(repository: PymojisRepositoryImpl) -> None:
    result = repository.replace("hi 😀", lambda e: f"<{e.name}>")
    assert result == "hi <grinning face>"


def test_replace_invalid_repl_raises(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(TypeError):
        repository.replace("hi 😀", 1234)  # type: ignore[arg-type]


def test_demojifie(repository: PymojisRepositoryImpl) -> None:
    assert repository.demojifie("hi 😀") == "hi :grinning_face:"


def test_demojifie_multiple(repository: PymojisRepositoryImpl) -> None:
    out = repository.demojifie("morning 😀 then 😪 night")
    assert out == "morning :grinning_face: then :sleepy_face: night"


def test_text_methods_wrong_type_raise(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(TypeError):
        repository.extract(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.count(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.strip(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.replace(123, "x")  # type: ignore[arg-type]


def test_contains_emojis_uses_scanner(repository: PymojisRepositoryImpl) -> None:
    # Regression: contains_emojis now goes through the same regex as extract.
    assert repository.contains_emojis("only zwj: 😵‍💫")
    assert not repository.contains_emojis("totally plain string")


# --- Phase 3: integration + family --------------------------------------


def test_to_codepoint_string_single(repository: PymojisRepositoryImpl) -> None:
    assert repository.to_codepoint_string("😀") == "U+1F600"


def test_to_codepoint_string_zwj(repository: PymojisRepositoryImpl) -> None:
    assert repository.to_codepoint_string("😵‍💫") == "U+1F635 U+200D U+1F4AB"


def test_to_codepoint_string_custom_sep_prefix(
    repository: PymojisRepositoryImpl,
) -> None:
    assert repository.to_codepoint_string("😀", sep="-", prefix="") == "1F600"


def test_to_codepoint_string_empty_raises(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(ValueError):
        repository.to_codepoint_string("")


def test_to_unicode_escape_single(repository: PymojisRepositoryImpl) -> None:
    assert repository.to_unicode_escape("😀") == r"\U0001F600"


def test_to_unicode_escape_multi(repository: PymojisRepositoryImpl) -> None:
    # All escapes are 8-digit \U form, even for ZWJ (U+200D) inside the sequence.
    assert repository.to_unicode_escape("😵‍💫") == r"\U0001F635\U0000200D\U0001F4AB"


def test_to_image_url_twemoji_default_svg(repository: PymojisRepositoryImpl) -> None:
    url = repository.to_image_url("😀")
    assert url == (
        "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/svg/1f600.svg"
    )


def test_to_image_url_twemoji_png(repository: PymojisRepositoryImpl) -> None:
    url = repository.to_image_url("😀", provider="twemoji", extension="png")
    assert url.endswith("/1f600.png")


def test_to_image_url_openmoji_strips_fe0f(
    repository: PymojisRepositoryImpl,
) -> None:
    # ❤️ = U+2764 U+FE0F; OpenMoji's repo stores it as 2764.svg
    url = repository.to_image_url("❤️", provider="openmoji")
    assert url == "https://openmoji.org/data/color/svg/2764.svg"


def test_to_image_url_unknown_provider_raises(
    repository: PymojisRepositoryImpl,
) -> None:
    with pytest.raises(ValueError):
        repository.to_image_url("😀", provider="emojione")  # type: ignore[arg-type]


def test_is_flag_country_flag(repository: PymojisRepositoryImpl) -> None:
    # 🇫🇷 = U+1F1EB U+1F1F7 (FR)
    assert repository.is_flag("\U0001f1eb\U0001f1f7")


def test_is_flag_dataset_flag(repository: PymojisRepositoryImpl) -> None:
    # 🏁 is in the Flags category but not an RIS pair.
    assert repository.is_flag("🏁")


def test_is_flag_not_a_flag(repository: PymojisRepositoryImpl) -> None:
    assert not repository.is_flag("😀")
    assert not repository.is_flag("hello")


def test_flag_for_uppercase(repository: PymojisRepositoryImpl) -> None:
    assert repository.flag_for("FR") == "\U0001f1eb\U0001f1f7"


def test_flag_for_lowercase(repository: PymojisRepositoryImpl) -> None:
    assert repository.flag_for("us") == "\U0001f1fa\U0001f1f8"


def test_flag_for_invalid_raises(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(ValueError):
        repository.flag_for("FRA")
    with pytest.raises(ValueError):
        repository.flag_for("12")


def test_country_of_country_flag(repository: PymojisRepositoryImpl) -> None:
    assert repository.country_of("\U0001f1eb\U0001f1f7") == "FR"


def test_country_of_non_flag_returns_none(repository: PymojisRepositoryImpl) -> None:
    assert repository.country_of("😀") is None
    assert repository.country_of("🏁") is None


# --- light-dataset behavior of full-only methods ---


def test_to_shortcode_light_returns_none(repository: PymojisRepositoryImpl) -> None:
    # Light dataset ships without shortcodes, so this is always None.
    assert repository.to_shortcode("😀") is None


def test_from_shortcode_light_returns_none(repository: PymojisRepositoryImpl) -> None:
    assert repository.from_shortcode(":grinning_face:") is None


def test_base_of_light_returns_none(repository: PymojisRepositoryImpl) -> None:
    assert repository.base_of("👍") is None


def test_skin_tones_light_returns_empty(repository: PymojisRepositoryImpl) -> None:
    assert repository.skin_tones("👍") == []


# --- full-dataset behavior, skipped if extra not installed ---


@pytest.fixture
def full_repo() -> PymojisRepositoryImpl:
    pytest.importorskip("pymojis_fulldata")
    repo = PymojisRepositoryImpl()
    repo.load_emojis(kind="full")
    return repo


def test_to_shortcode_full(full_repo: PymojisRepositoryImpl) -> None:
    assert full_repo.to_shortcode("😀") == ":grinning_face:"


def test_to_shortcode_full_unknown_set(full_repo: PymojisRepositoryImpl) -> None:
    assert full_repo.to_shortcode("😀", set_name="slack") is None


def test_from_shortcode_full(full_repo: PymojisRepositoryImpl) -> None:
    assert full_repo.from_shortcode(":grinning_face:") == "😀"


def test_from_shortcode_full_with_set(full_repo: PymojisRepositoryImpl) -> None:
    assert full_repo.from_shortcode(":grinning_face:", set_name="github") == "😀"
    assert full_repo.from_shortcode(":grinning_face:", set_name="nope") is None


def test_base_of_full_variant(full_repo: PymojisRepositoryImpl) -> None:
    # 👋🏻 (waving hand light skin tone) → 👋
    assert full_repo.base_of("\U0001f44b\U0001f3fb") == "👋"


def test_base_of_full_base_returns_none(full_repo: PymojisRepositoryImpl) -> None:
    assert full_repo.base_of("👋") is None


def test_skin_tones_full_from_base(full_repo: PymojisRepositoryImpl) -> None:
    tones = full_repo.skin_tones("👋")
    # 5 Fitzpatrick variants
    assert len(tones) == 5


def test_skin_tones_full_from_variant(full_repo: PymojisRepositoryImpl) -> None:
    # Asking from a variant returns the other variants under the same base.
    tones = full_repo.skin_tones("\U0001f44b\U0001f3fb")
    assert len(tones) == 5


# --- Phase 4: discovery -------------------------------------------------


def test_search_by_exact_name(repository: PymojisRepositoryImpl) -> None:
    results = repository.search("grinning face")
    assert results[0].name == "grinning face"


def test_search_by_substring(repository: PymojisRepositoryImpl) -> None:
    results = repository.search("grin")
    assert len(results) > 0
    assert all(
        "grin" in e.name.lower() or any("grin" in k.lower() for k in e.keywords)
        for e in results
    )


def test_search_no_match(repository: PymojisRepositoryImpl) -> None:
    assert repository.search("zzzzzzz_no_such_thing") == []


def test_search_empty_query(repository: PymojisRepositoryImpl) -> None:
    assert repository.search("") == []
    assert repository.search("   ") == []


def test_search_limit_caps_results(repository: PymojisRepositoryImpl) -> None:
    results = repository.search("face", limit=3)
    assert len(results) == 3


def test_search_zero_limit_returns_empty(repository: PymojisRepositoryImpl) -> None:
    assert repository.search("face", limit=0) == []


def test_search_negative_limit_raises(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(ValueError):
        repository.search("face", limit=-1)


def test_suggest_returns_relatives(repository: PymojisRepositoryImpl) -> None:
    # 😀 (grinning face) → expect other smileys in the suggestion
    results = repository.suggest("😀")
    assert len(results) > 0
    # All suggestions should share something with grinning face's structure.
    assert all(e.emoji != "😀" for e in results)


def test_suggest_unknown_returns_empty(repository: PymojisRepositoryImpl) -> None:
    assert repository.suggest("not-an-emoji") == []


def test_suggest_limit(repository: PymojisRepositoryImpl) -> None:
    assert len(repository.suggest("😀", limit=2)) <= 2


def test_categories_returns_all_present(repository: PymojisRepositoryImpl) -> None:
    cats = repository.categories()
    assert "Smileys & Emotion" in cats
    assert "Flags" in cats
    # No duplicates
    assert len(cats) == len(set(cats))


def test_sub_categories_all(repository: PymojisRepositoryImpl) -> None:
    subs = repository.sub_categories()
    assert "face-smiling" in subs
    assert len(subs) == len(set(subs))


def test_sub_categories_filtered(repository: PymojisRepositoryImpl) -> None:
    subs = repository.sub_categories("Smileys & Emotion")
    assert "face-smiling" in subs
    # Should NOT contain a subcategory from a different category
    assert not any(s.startswith("hand-") for s in subs)


def test_sub_categories_unknown_category_returns_empty(
    repository: PymojisRepositoryImpl,
) -> None:
    assert repository.sub_categories("Nonexistent") == []


def test_get_by_subcategory(repository: PymojisRepositoryImpl) -> None:
    results = repository.get_by_subcategory("face-smiling")
    assert len(results) > 0
    assert all(e.sub_category == "face-smiling" for e in results)


def test_get_by_subcategory_unknown_returns_empty(
    repository: PymojisRepositoryImpl,
) -> None:
    assert repository.get_by_subcategory("nonexistent") == []


def test_discovery_wrong_type_raises(repository: PymojisRepositoryImpl) -> None:
    with pytest.raises(TypeError):
        repository.search(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.suggest(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.sub_categories(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.get_by_subcategory(123)  # type: ignore[arg-type]


def test_integration_methods_wrong_type_raise(
    repository: PymojisRepositoryImpl,
) -> None:
    with pytest.raises(TypeError):
        repository.to_shortcode(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.from_shortcode(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.base_of(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.is_flag(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.flag_for(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        repository.country_of(123)  # type: ignore[arg-type]
