# pymojis

[![PyPI version](https://img.shields.io/pypi/v/pymojis.svg)](https://pypi.org/project/pymojis/)
[![Python versions](https://img.shields.io/pypi/pyversions/pymojis.svg)](https://pypi.org/project/pymojis/)
[![License: MIT](https://img.shields.io/pypi/l/pymojis.svg)](https://github.com/pallandir/pymojis/blob/main/LICENSE)
[![CI](https://github.com/pallandir/pymojis/actions/workflows/github_ci.yaml/badge.svg)](https://github.com/pallandir/pymojis/actions/workflows/github_ci.yaml)

A small, type-safe Python library for working with emojis: search them by
name / code / character, transform text, detect emojis in strings, and
convert to HTML.

- **Zero runtime dependencies.**
- **Two install sizes**: a tiny default (~230 KB of data) or the full
  Unicode dataset (~1 MB) via the `[full]` extra.
- **Strict typing** — `py.typed`, full mypy strict compliance.
- **Fail-fast API** — bad input raises immediately, no silent `None`
  returns or warnings.

## Install

```bash
pip install pymojis              # lightweight: ~1900 emojis
pip install 'pymojis[full]'      # full Unicode coverage: ~3790 emojis
```

Requires **Python 3.12+**.

## Quick start

```python
from pymojis import PymojisManager

manager = PymojisManager()

# Pick random emojis
print([e.emoji for e in manager.get_random(length=3)])
# → ['😊', '🎉', '🌟']

# Look up by name / code / character
manager.get_by_name("grinning face with smiling eyes")  # → '😄'
manager.get_by_code("1F604")                            # → '😄'
manager.get_by_emoji("😊")                              # → Emoji(...)

# Replace whole-word matches in text
manager.emojifie("I'm sleepy")
# → "I'm 😪"

# Detection
manager.contains_emojis("hello 👋")    # → True
manager.is_emoji("😄")                 # → True
manager.is_emoji("😄😊")               # → False

# HTML hex references
manager.to_html("😵‍💫")
# → "&#x1F635;&#x200D;&#x1F4AB;"

# Text operations
manager.extract("hi 😀 and 😪")            # → [Emoji('grinning face'), Emoji('sleepy face')]
manager.count("😀😀😪")                    # → 3
manager.strip("hi 😀 there")               # → "hi  there"
manager.replace("hi 😀", "[e]")            # → "hi [e]"
manager.replace("hi 😀", lambda e: e.name) # → "hi grinning face"
manager.demojifie("hi 😀")                 # → "hi :grinning_face:"
```

To use the full Unicode dataset:

```python
manager = PymojisManager(use_full_dataset=True)
# Requires `pip install 'pymojis[full]'`. Raises DatasetNotFoundError
# with installation instructions otherwise.
```

## API

| Method | Returns | Notes |
|---|---|---|
| `get_random(categories=None, length=1, exclude=None)` | `list[Emoji]` | `categories` takes precedence over `exclude`. |
| `get_all_emojis(exclude=None)` | `list[Emoji]` | `exclude` accepts `"complex"` or a list of categories. |
| `get_by_code(code)` | `str \| None` | Single-codepoint lookup. Case-insensitive. |
| `get_by_name(name)` | `str \| None` | Full-name lookup. Case-insensitive. |
| `get_by_category(category)` | `list[str]` | All emojis in a category. |
| `get_by_emoji(emoji)` | `Emoji \| None` | Reverse lookup from character to record. |
| `contains_emojis(text)` | `bool` | True if `text` contains at least one known emoji. |
| `is_emoji(text)` | `bool` | True if `text.strip()` is a single known emoji. |
| `emojifie(text)` | `str` | Replace whole words with emojis (whose name *contains* that word). |
| `to_html(emoji)` | `str` | Encode each codepoint as `&#xHEX;`. |
| `extract(text)` | `list[Emoji]` | All emojis in `text`, in order of appearance. |
| `find(text)` | `Iterator[tuple[Emoji, int, int]]` | `(emoji, start, end)` for each match — indices over the raw string. |
| `count(text)` | `int` | Number of emoji occurrences in `text`. |
| `count_by(text)` | `dict[Emoji, int]` | Histogram of `{Emoji: count}`. |
| `strip(text)` | `str` | Remove every emoji (no whitespace collapsing). |
| `replace(text, repl)` | `str` | `repl` is either a literal string or `Callable[[Emoji], str]`. |
| `demojifie(text)` | `str` | Rewrite each emoji as `:slugified_name:`. |

All methods raise `TypeError` on non-`str` arguments — no silent `None`.

### Text scanning

`extract` / `find` / `count` / `count_by` / `strip` / `replace` / `demojifie`
all share a single longest-match-first scanner built at load time: ZWJ
sequences and skin-tone composites are matched as whole units, so
`extract("👍🏽")` returns the medium-skin-tone variant — never the bare
thumbs-up plus a separate modifier.

### Categories

```python
from pymojis import Categories

Categories  # type alias of all valid categories:
#   "Smileys & Emotion", "People & Body", "Animals & Nature",
#   "Food & Drink", "Activities", "Travel & Places", "Objects",
#   "Symbols", "Flags", "Component"
```

### `Emoji` data model

```python
from pymojis import Emoji

@dataclass-like
class Emoji:
    id: str            # auto-generated UUID
    emoji: str         # the character itself, e.g. "😄"
    name: str          # e.g. "grinning face with smiling eyes"
    code: list[str]    # one or more Unicode codepoints, e.g. ["1F604"]
                       #   (multi-codepoint emojis like ZWJ sequences have len > 1)
    category: str      # e.g. "Smileys & Emotion"
    sub_category: str  # e.g. "face-smiling"
```

## Notes on `emojifie`

`emojifie` does whole-word matching. Each word in the input is looked up in
an index of emoji-name tokens. Tokens shorter than 3 characters are skipped
(otherwise pronouns like "I" and "m" would be replaced by ℹ and Ⓜ). When a
word matches multiple emojis, the first one (in dataset order) wins.

```python
manager.emojifie("I'm sleepy")           # → "I'm 😪"  (sleepy → "sleepy face")
manager.emojifie("zzzz xyzzy")           # → "zzzz xyzzy"  (no match, unchanged)
```

## Releases (maintainer notes)

This repo publishes **two** packages on every git tag: `pymojis` and
`pymojis-fulldata`. Both must share the same version.

To cut a release:

```bash
# 1. Bump version in BOTH pyproject files
$EDITOR pyproject.toml                                  # version = "X.Y.Z"
$EDITOR packages/pymojis-fulldata/pyproject.toml        # version = "X.Y.Z"
# Also bump the [full] extra dependency pin in pyproject.toml.

# 2. Commit, tag, push
git commit -am "Release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

CI runs the full `make ci` pipeline (lint, format, typecheck, tests,
build both wheels, twine check) and publishes via PyPI Trusted Publishing
(OIDC — no API tokens). One-time setup: register both projects as
Trusted Publishers on https://pypi.org pointing at this repo and the
workflow `.github/workflows/github_ci.yaml`.

## Development

A `Makefile` wraps the common workflows:

```bash
make install       # uv sync --extra dev --frozen
make lint          # ruff check
make format-check  # ruff format --check
make typecheck     # mypy src
make test          # pytest
make build         # build both wheels into dist/
make twine-check   # twine check dist/*
make ci            # lint + format-check + typecheck + test + build + twine-check
make clean         # remove dist/, build/, *.egg-info
```

`pre-commit` is configured: `uv run pre-commit install` once, and the same
checks run on every commit.

## Contributing

Issues and PRs welcome. Please run the full check suite above before
opening a PR.

## License

MIT — see [LICENSE](LICENSE).

The bundled emoji metadata derives from the work of
[Chalda Pnuzig](https://github.com/chalda-pnuzig/emojis.json) (ISC License,
see `third_party/`).
