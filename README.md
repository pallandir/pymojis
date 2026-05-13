# pymojis

[![PyPI version](https://img.shields.io/pypi/v/pymojis.svg)](https://pypi.org/project/pymojis/)
[![Python versions](https://img.shields.io/pypi/pyversions/pymojis.svg)](https://pypi.org/project/pymojis/)
[![License: MIT](https://img.shields.io/pypi/l/pymojis.svg)](https://github.com/pallandir/pymojis/blob/main/LICENSE)
[![CI](https://github.com/pallandir/pymojis/actions/workflows/github_ci.yaml/badge.svg)](https://github.com/pallandir/pymojis/actions/workflows/github_ci.yaml)

A tiny Python library for working with emojis. Look them up by name or
codepoint, pick a random one, check if a string contains any, pull all
the emojis out of a chat message, convert to HTML or to a Twemoji URL —
that kind of thing.

I wrote it because every time I needed "just a list of emojis with
their names" I ended up vendoring a JSON file from somewhere. This is
that JSON file with a few helpers on top, no runtime dependencies, and
types that actually work in mypy strict.

## Install

```bash
pip install pymojis              # ~1900 emojis, ~230 KB of data
pip install 'pymojis[full]'      # full Unicode set, ~3790 emojis (~1 MB)
```

Python 3.12+.

The default dataset covers the everyday stuff. The `[full]` extra pulls
in `pymojis-fulldata`, which ships every emoji including the skin-tone
variants, ZWJ sequences, CLDR keywords, and GitHub-style shortcodes —
useful if you care about completeness, overkill if you don't.

## Using it

```python
from pymojis import PymojisManager

m = PymojisManager()

m.get_random(length=3)                                  # 3 random Emoji objects
m.get_by_name("grinning face with smiling eyes")        # → '😄'
m.get_by_code("1F604")                                  # → '😄'
m.get_by_emoji("😊")                                    # → Emoji(...)

m.contains_emojis("hello 👋")                            # → True
m.is_emoji("😄")                                         # → True

m.extract("hi 😀 and 😪")                                # → [Emoji('grinning face'), Emoji('sleepy face')]
m.strip("hi 😀 there")                                   # → "hi  there"
m.replace("hi 😀", lambda e: f"[{e.name}]")              # → "hi [grinning face]"

m.flag_for("FR")                                         # → '🇫🇷'
m.country_of("🇫🇷")                                       # → 'FR'

m.to_html("😵‍💫")                                        # → "&#x1F635;&#x200D;&#x1F4AB;"
m.to_unicode_escape("😀")                                # → "\\U0001F600"
m.to_image_url("😀")                                     # → twemoji CDN URL
```

Switching to the full set:

```python
m = PymojisManager(use_full_dataset=True)
# Raises DatasetNotFoundError (with the pip command) if [full] isn't installed.
```

## What's on the manager

**Lookup and random**

- `get_random(categories=None, length=1, exclude=None)` — random pick. `categories` wins over `exclude`.
- `get_all_emojis(exclude=None)` — every emoji. `exclude` accepts `"complex"` (drop multi-codepoint) or a list of categories.
- `get_by_code(code)`, `get_by_name(name)` — single-codepoint / full-name lookup, case-insensitive.
- `get_by_category(category)`, `get_by_subcategory(name)`, `get_by_emoji(emoji)`.
- `categories()`, `sub_categories(category=None)` — list what the dataset actually contains.

**Detection and scanning** — all share one longest-match-first regex,
so `👍🏽` matches as one unit, not "thumbs up + skin tone modifier".

- `contains_emojis(text)` / `is_emoji(text)`.
- `extract(text)` → `list[Emoji]` in order of appearance.
- `find(text)` → iterator of `(emoji, start, end)`.
- `count(text)`, `count_by(text)`.
- `strip(text)`, `replace(text, repl)` — `repl` is a literal string or `Callable[[Emoji], str]`.
- `demojifie(text)` — rewrites each emoji as `:slugified_name:`.

**Format and convert**

- `to_html(emoji)` — `&#xHEX;` references.
- `to_codepoint_string(emoji, sep=" ", prefix="U+")` — `"U+1F635 U+200D U+1F4AB"`.
- `to_unicode_escape(emoji)` — `\U0001F600` form, safe to paste into Python source.
- `to_image_url(emoji, provider="twemoji" | "openmoji", extension="svg" | "png")` — public CDN URLs.

**Flags** — these don't need any dataset, they're computed from codepoints.

- `is_flag(emoji)` — Flags category or a bare Regional Indicator Symbol pair.
- `flag_for(country_code)` — `"FR"` → `"🇫🇷"`. Raises on invalid input.
- `country_of(emoji)` — `"🇫🇷"` → `"FR"`. `None` for non-flags (including tag-sequence subdivision flags).

**Family and shortcodes** — only meaningful with the `[full]` dataset.
On the light bundle these return `None` / `[]` because the data isn't
there (size budget), not because the logic is missing.

- `base_of(emoji)` — `"👍🏽"` → `"👍"`.
- `skin_tones(emoji)` — all five Fitzpatrick siblings; works whether you pass the base or a variant.
- `to_shortcode(emoji, set_name="github")`, `from_shortcode(code, set_name=None)`.

**Search**

- `search(query, limit=10)` — ranked: exact name, then name substring, then name token, then keyword. Falls back to name-only on the light dataset (no keywords).
- `suggest(emoji, limit=5)` — same subcategory first, then keyword overlap, then same category.

**Text replacement based on names**

- `emojifie(text)` — replaces whole words with an emoji whose name contains that word (see below).

Anything that takes a string and gets something else raises `TypeError`
on the spot. No silent `None`, no warnings to ignore.

### Categories

```python
from pymojis import Categories
# Literal type of: "Smileys & Emotion", "People & Body", "Animals & Nature",
# "Food & Drink", "Activities", "Travel & Places", "Objects", "Symbols",
# "Flags", "Component"
```

### The `Emoji` record

```python
Emoji(
    id=...,                          # UUID, generated on construction
    emoji="👍🏽",
    name="thumbs up: medium skin tone",
    code=["1F44D", "1F3FD"],         # list because ZWJ sequences have multiple codepoints
    category="People & Body",
    sub_category="hand-fingers-closed",
    unicode_version="1.0",
    qualification="fully-qualified", # or "minimally-qualified", "unqualified", "component"
    base_code=["1F44D"],             # None for base emojis; set for skin-tone variants
    keywords=["hand", "thumb", "up"],          # full dataset only; [] on light
    shortcodes={"github": ":thumbs_up_..."},   # full dataset only; {} on light
)
```

`unicode_version`, `qualification`, and `base_code` come from
`emoji-test.txt`; `keywords` and `shortcodes` are added from the CLDR
annotations during the dataset build (see `scripts/build_dataset.py`).

## CLI

There's a small command-line tool — call it as `pymojis` once installed,
or `python -m pymojis` without installing the script.

```bash
pymojis search grin              # find emojis by name / keyword
pymojis search face --limit 5
pymojis random --length 3        # 3 random emoji glyphs
pymojis random --length 1 -v     # verbose: emoji + name + category
pymojis info 😀                  # everything we know about an emoji
pymojis --full search "thumbs"   # use the full dataset for richer search
```

Exit codes: `0` on success, `1` when nothing matched (or the emoji's
unknown), `2` when argparse didn't like your invocation.

## A note on `emojifie`

It's whole-word matching against a token index built from emoji names.
Tokens shorter than 3 characters are skipped — otherwise "I" and "m"
would get eaten by ℹ and Ⓜ, which is funny exactly once. If a word
matches several emojis, the first one in dataset order wins.

```python
m.emojifie("I'm sleepy")     # → "I'm 😪"
m.emojifie("zzzz xyzzy")     # → "zzzz xyzzy"
```

It still only looks at words that appear *in the emoji name*, so
`"happy"` doesn't match 😄 — for keyword-aware search use `m.search`
instead (with the `[full]` dataset, which ships the CLDR keywords).

## Development

There's a `Makefile` for the usual chores:

```bash
make install       # uv sync --extra dev --frozen
make lint
make format-check
make typecheck
make test
make build         # builds both wheels
make ci            # everything above
```

`pre-commit` is set up — `uv run pre-commit install` once and the same
checks run on commit.

## Contributing

Issues and PRs welcome. Run `make ci` before opening one.

## License

MIT — see [LICENSE](LICENSE).

The bundled emoji metadata is derived from
[Chalda Pnuzig's emojis.json](https://github.com/chalda-pnuzig/emojis.json)
(ISC, see `third_party/`). Keywords and shortcode hints come from the
[Unicode CLDR](https://cldr.unicode.org/) annotations (Unicode License V3,
see `third_party/cldr/LICENSE` and `third_party/NOTICE.txt`). Thanks to
both projects for doing the tedious part.
