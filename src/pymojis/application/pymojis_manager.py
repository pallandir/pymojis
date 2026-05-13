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
