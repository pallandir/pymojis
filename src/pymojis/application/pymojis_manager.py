from collections.abc import Callable, Iterator
from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


class PymojisManager:
    """High-level facade for emoji search, transformation, and detection.

    By default the manager loads the lightweight bundled dataset (~228 KB).
    Pass ``use_full_dataset=True`` to load the full dataset, which requires
    the optional ``pymojis-fulldata`` package (``pip install 'pymojis[full]'``).
    """

    def __init__(self, *, use_full_dataset: bool = False) -> None:
        self.repository = PymojisRepositoryImpl()
        self.repository.load_emojis(kind="full" if use_full_dataset else "light")

    def get_random(
        self,
        categories: list[Categories] | None = None,
        length: int = 1,
        exclude: Literal["complex"] | list[Categories] | None = None,
    ) -> list[Emoji]:
        """Return ``length`` random ``Emoji`` objects, optionally filtered.

        Args:
            categories: If provided, only emojis from these categories are
                considered. Takes precedence over ``exclude``.
            length: Number of emojis to return. Capped at the size of the pool.
            exclude: ``"complex"`` to exclude multi-codepoint emojis (skin
                tones, ZWJ sequences), or a list of categories to skip.

        Example:
            >>> manager = PymojisManager()
            >>> [e.emoji for e in manager.get_random(length=2)]  # doctest: +SKIP
            ['😊', '🌟']
        """
        return self.repository.get_random_emojis(categories, length, exclude)

    def get_all_emojis(
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]:
        """Return every loaded ``Emoji``, optionally filtered by ``exclude``."""
        return self.repository.get_all(exclude)

    def get_by_code(self, code: str) -> str | None:
        """Return the emoji character matching the given Unicode codepoint.

        Only single-codepoint emojis are addressable this way. Returns
        ``None`` if no match.
        """
        return self.repository.get_by_code(code)

    def get_by_name(self, name: str) -> str | None:
        """Return the emoji character whose full name equals ``name``.

        Matching is case-insensitive. Returns ``None`` if no match.
        """
        return self.repository.get_by_name(name)

    def get_by_category(self, category: Categories) -> list[str]:
        """Return all emoji characters in the given category."""
        return self.repository.get_by_category(category)

    def get_by_emoji(self, emoji: str) -> Emoji | None:
        """Return the ``Emoji`` object whose character equals ``emoji``."""
        return self.repository.get_by_emoji(emoji)

    def contains_emojis(self, text: str) -> bool:
        """Return ``True`` if ``text`` contains at least one known emoji."""
        return self.repository.contains_emojis(text)

    def is_emoji(self, text: str) -> bool:
        """Return ``True`` if ``text`` (after stripping) is a single known emoji."""
        return self.repository.is_emoji(text)

    def emojifie(self, text: str) -> str:
        """Replace each whole word in ``text`` whose lowercase form is a token
        of an emoji name with that emoji.

        Tokens are matched against the first word of any emoji's name (e.g.
        ``"sleepy"`` matches the emoji named ``"sleepy face"``). Words that
        match no emoji are left unchanged.

        Example:
            >>> manager = PymojisManager()
            >>> manager.emojifie("I'm sleepy")  # doctest: +SKIP
            "I'm 😪"
        """
        return self.repository.emojifie(text)

    def to_html(self, emoji: str) -> str:
        """Return ``emoji`` as a sequence of HTML hex character references.

        Multi-codepoint emojis (ZWJ sequences, variation selectors) are
        encoded codepoint by codepoint.

        Example:
            >>> PymojisManager().to_html("😪")  # doctest: +SKIP
            '&#x1F62A;'
        """
        return self.repository.to_html(emoji)

    def extract(self, text: str) -> list[Emoji]:
        """Return all emojis present in ``text``, in order of appearance.

        ZWJ sequences and skin-tone composites are matched as whole units
        (e.g. ``"👍🏽"`` returns the medium-skin-tone variant, not the bare
        thumbs-up plus a separate modifier).
        """
        return self.repository.extract(text)

    def find(self, text: str) -> Iterator[tuple[Emoji, int, int]]:
        """Yield ``(emoji, start, end)`` for each emoji match in ``text``.

        Indices are over the raw string (the same indices ``str.find`` uses),
        so callers can slice ``text[start:end]`` to recover the matched glyph.
        """
        return self.repository.find(text)

    def count(self, text: str) -> int:
        """Return the total number of emoji occurrences in ``text``."""
        return self.repository.count(text)

    def count_by(self, text: str) -> dict[Emoji, int]:
        """Return a histogram of ``{Emoji: occurrence_count}`` for ``text``."""
        return self.repository.count_by(text)

    def strip(self, text: str) -> str:
        """Return ``text`` with every emoji removed (no whitespace collapsing)."""
        return self.repository.strip(text)

    def replace(self, text: str, repl: str | Callable[[Emoji], str]) -> str:
        """Replace each emoji in ``text``.

        Args:
            repl: A literal string used for every match, or a callable
                ``(Emoji) -> str`` invoked once per match.

        Example:
            >>> PymojisManager().replace("Hello 😀", "[emoji]")  # doctest: +SKIP
            'Hello [emoji]'
        """
        return self.repository.replace(text, repl)

    def demojifie(self, text: str) -> str:
        """Return ``text`` with each emoji rewritten as ``:slugified_name:``.

        Slugification lowercases the emoji name and replaces runs of
        non-alphanumeric characters with single underscores.

        Example:
            >>> PymojisManager().demojifie("hi 😀")  # doctest: +SKIP
            'hi :grinning_face:'
        """
        return self.repository.demojifie(text)

    def to_codepoint_string(
        self, emoji: str, sep: str = " ", prefix: str = "U+"
    ) -> str:
        """Format an emoji as its codepoint string, e.g. ``'U+1F600'``.

        Multi-codepoint emojis are space-separated by default.

        Example:
            >>> PymojisManager().to_codepoint_string("😀")  # doctest: +SKIP
            'U+1F600'
        """
        return self.repository.to_codepoint_string(emoji, sep=sep, prefix=prefix)

    def to_unicode_escape(self, emoji: str) -> str:
        r"""Format an emoji as Python ``\\U`` escapes, suitable for source code.

        Always emits 8-hex-digit ``\\U`` escapes (codepoints above U+FFFF
        cannot use the 4-digit ``\\u`` form).

        Example:
            >>> PymojisManager().to_unicode_escape("😀")  # doctest: +SKIP
            '\\U0001F600'
        """
        return self.repository.to_unicode_escape(emoji)

    def to_image_url(
        self,
        emoji: str,
        provider: Literal["twemoji", "openmoji"] = "twemoji",
        extension: Literal["svg", "png"] = "svg",
    ) -> str:
        """Return a public CDN URL for the emoji's image at the given provider.

        ``twemoji`` keeps Variation-Selector-16 (``FE0F``) in the filename;
        ``openmoji`` strips it per their repo convention.
        """
        return self.repository.to_image_url(emoji, provider, extension)

    def to_shortcode(self, emoji: str, set_name: str = "github") -> str | None:
        """Return the emoji's shortcode for the given vendor set, or ``None``.

        Requires the full dataset for any non-trivial result — the light
        dataset ships without shortcodes, so this always returns ``None``
        there.
        """
        return self.repository.to_shortcode(emoji, set_name)

    def from_shortcode(self, code: str, set_name: str | None = None) -> str | None:
        """Reverse lookup: shortcode (e.g. ``':grinning_face:'``) → emoji.

        With ``set_name=None``, returns the first match across all vendor
        sets. Returns ``None`` if no match.
        """
        return self.repository.from_shortcode(code, set_name)

    def base_of(self, emoji: str) -> str | None:
        """Return the base emoji for a skin-tone or ZWJ variant.

        ``base_of('👍🏽')`` → ``'👍'``. Returns ``None`` for emojis that
        have no parent (base emojis themselves, or unknown input).
        """
        return self.repository.base_of(emoji)

    def skin_tones(self, emoji: str) -> list[str]:
        """Return all skin-tone variants of the same base as ``emoji``.

        Works whether ``emoji`` is the base or one of the variants. Empty
        list if the emoji has no skin-tone family.
        """
        return self.repository.skin_tones(emoji)

    def is_flag(self, emoji: str) -> bool:
        """Return ``True`` if ``emoji`` is a country flag.

        Accepts both dataset-known flags (Flags category) and any bare
        Regional Indicator Symbol pair, even ones not yet in the dataset.
        """
        return self.repository.is_flag(emoji)

    def flag_for(self, country_code: str) -> str:
        """Return the flag emoji for an ISO 3166-1 alpha-2 country code.

        Example:
            >>> PymojisManager().flag_for('FR')  # doctest: +SKIP
            '🇫🇷'

        Raises ``ValueError`` for inputs that are not 2 ASCII letters.
        """
        return self.repository.flag_for(country_code)

    def country_of(self, emoji: str) -> str | None:
        """Return the ISO 3166-1 alpha-2 country code for a flag emoji, or ``None``.

        Only the 2-Regional-Indicator-Symbol form is decoded; subdivision
        flags (England, Scotland, Wales) use tag sequences and return ``None``.
        """
        return self.repository.country_of(emoji)
