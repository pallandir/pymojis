"""Regenerate the bundled emoji datasets from Chalda + vendored CLDR sources.

Pure transform. Never accesses the network: the CLDR source files at
``third_party/cldr/`` are refreshed separately by the ``refresh-dataset``
GitHub workflow.

Inputs:
  src/pymojis/infrastructure/data/emoji_data.json
  packages/pymojis-fulldata/src/pymojis_fulldata/data/full_emoji_data.json
  third_party/cldr/emoji-test.txt
  third_party/cldr/en.xml

Outputs: the same two dataset files, overwritten with the enriched schema.

Run via ``make data``.
"""

import json
import re
import xml.etree.ElementTree as ET  # noqa: S405  vendored CLDR data, trusted input
from pathlib import Path
from typing import Any

# Top-level keys produced by this script. Stripped before re-enrichment so the
# script is idempotent (running it on its own previous output yields the same
# result as running it on a pristine Chalda dataset).
_ENRICHMENT_KEYS = frozenset({"emojis", "@cldr", "indices"})

REPO_ROOT = Path(__file__).resolve().parent.parent
CLDR_DIR = REPO_ROOT / "third_party" / "cldr"
EMOJI_TEST = CLDR_DIR / "emoji-test.txt"
ANNOTATIONS_XML = CLDR_DIR / "en.xml"

LIGHT_JSON = (
    REPO_ROOT / "src" / "pymojis" / "infrastructure" / "data" / "emoji_data.json"
)
FULL_JSON = (
    REPO_ROOT
    / "packages"
    / "pymojis-fulldata"
    / "src"
    / "pymojis_fulldata"
    / "data"
    / "full_emoji_data.json"
)

# Fitzpatrick skin-tone modifier codepoints.
SKIN_TONES = frozenset({"1F3FB", "1F3FC", "1F3FD", "1F3FE", "1F3FF"})

# Matches a data line in emoji-test.txt, e.g.:
#   1F600                                                  ; fully-qualified     # 😀 E1.0 grinning face
_EMOJI_TEST_LINE = re.compile(
    r"^([0-9A-F ]+);\s*([\w-]+)\s*#\s*(\S+)\s+E(\d+\.\d+)\s+(.+)$",
    re.IGNORECASE,
)

# Matches the "# Version: X.Y" header inside emoji-test.txt.
_EMOJI_TEST_VERSION = re.compile(r"^#\s*Version:\s*(\d+\.\d+)", re.MULTILINE)

# Non-alphanumeric chars are stripped, separators collapse to underscore.
_SHORTCODE_STRIP = re.compile(r"[^a-z0-9_\s-]")
_SHORTCODE_SEP = re.compile(r"[\s\-:,]+")


def parse_unicode_version(emoji_test_path: Path) -> str:
    content = emoji_test_path.read_text(encoding="utf-8")
    m = _EMOJI_TEST_VERSION.search(content)
    if not m:
        raise ValueError(f"Could not parse '# Version:' header from {emoji_test_path}")
    return m.group(1)


def parse_emoji_test(path: Path) -> dict[str, dict[str, Any]]:
    """Map each emoji char to its CLDR qualification + Unicode version + name.

    Keyed by emoji character (not codepoint) because Chalda's ``code`` field
    sometimes lists the unqualified form (e.g. ``["2764"]`` for red heart)
    while emoji-test.txt's canonical entry is fully-qualified (``2764 FE0F``).
    The emoji char itself is the stable join key.
    """
    result: dict[str, dict[str, Any]] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = _EMOJI_TEST_LINE.match(line)
        if not m:
            continue
        codes_str, qual, emoji_char, version, name = m.groups()
        codes = codes_str.strip().upper().split()
        # Prefer fully-qualified when the same emoji appears in multiple forms.
        existing = result.get(emoji_char)
        if existing and existing["qualification"] == "fully-qualified":
            continue
        result[emoji_char] = {
            "codes": codes,
            "unicode_version": version,
            "qualification": qual,
            "name": name.strip(),
        }
    return result


def parse_annotations(path: Path) -> dict[str, list[str]]:
    """Map each emoji char to its CLDR keyword list (skips ``type="tts"``)."""
    tree = ET.parse(path)  # noqa: S314  vendored CLDR data, trusted input
    keywords: dict[str, list[str]] = {}
    for ann in tree.iter("annotation"):
        if ann.get("type") == "tts":
            continue
        cp = ann.get("cp")
        if cp and ann.text:
            kws = [k.strip() for k in ann.text.split("|") if k.strip()]
            if kws:
                keywords[cp] = kws
    return keywords


def derive_base_code(code: list[str]) -> list[str] | None:
    """Return the base codepoint sequence by stripping skin-tone modifiers.

    Returns ``None`` when the emoji has no skin-tone variant (i.e. it is
    already a base form), or when stripping leaves an empty sequence (the
    skin-tone modifier itself is its own record in the Component category).
    """
    if not any(c in SKIN_TONES for c in code):
        return None
    stripped = [c for c in code if c not in SKIN_TONES]
    return stripped or None


def derive_shortcode(name: str) -> str:
    """Derive a GitHub-style ``:snake_case:`` shortcode from an emoji name.

    Heuristic — matches GitHub's convention for ~90% of emojis. Future
    refreshes can swap in a vendored shortcode list if exact parity is
    needed.
    """
    s = name.lower()
    s = _SHORTCODE_STRIP.sub("", s)
    s = _SHORTCODE_SEP.sub("_", s).strip("_")
    return f":{s}:"


def enrich_record(
    record: dict[str, Any],
    emoji_test: dict[str, dict[str, Any]],
    annotations: dict[str, list[str]],
    *,
    full: bool,
) -> dict[str, Any]:
    """Take one Chalda record and produce an enriched record under the v2 schema."""
    code = record["code"]
    emoji = record["emoji"]
    name = record["name"]

    test_data = emoji_test.get(emoji)
    if test_data is None:
        raise ValueError(
            f"No emoji-test.txt entry for emoji {emoji!r} "
            f"(code={code}, name={name!r}). "
            "Chalda dataset may be newer than vendored CLDR — refresh CLDR sources."
        )

    out: dict[str, Any] = {
        "code": code,
        "emoji": emoji,
        "name": name,
        "unicode_version": test_data["unicode_version"],
        "qualification": test_data["qualification"],
        "base_code": derive_base_code(code),
    }
    if full:
        out["keywords"] = annotations.get(emoji, [])
        out["shortcodes"] = {"github": derive_shortcode(name)}
    return out


def enrich_dataset(
    source_path: Path,
    emoji_test: dict[str, dict[str, Any]],
    annotations: dict[str, list[str]],
    unicode_version: str,
    *,
    full: bool,
) -> dict[str, Any]:
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    if "emojis" not in raw:
        raise ValueError(f"{source_path} missing required top-level 'emojis' key")

    enriched: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for category, subcats in raw["emojis"].items():
        enriched[category] = {}
        for subcat, records in subcats.items():
            enriched[category][subcat] = [
                enrich_record(r, emoji_test, annotations, full=full) for r in records
            ]

    out: dict[str, Any] = {k: v for k, v in raw.items() if k not in _ENRICHMENT_KEYS}
    out["@cldr"] = f"Unicode {unicode_version} (vendored CLDR annotations)"
    out["emojis"] = enriched
    return out


def write_dataset(path: Path, data: dict[str, Any]) -> int:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path.stat().st_size


def main() -> None:
    print(f"Reading CLDR sources from {CLDR_DIR}")  # noqa: T201
    unicode_version = parse_unicode_version(EMOJI_TEST)
    print(f"  unicode version: {unicode_version}")  # noqa: T201
    emoji_test = parse_emoji_test(EMOJI_TEST)
    print(f"  emoji-test.txt:  {len(emoji_test)} records")  # noqa: T201
    annotations = parse_annotations(ANNOTATIONS_XML)
    print(f"  annotations:     {len(annotations)} records")  # noqa: T201

    print(f"\nEnriching light dataset: {LIGHT_JSON.relative_to(REPO_ROOT)}")  # noqa: T201
    light = enrich_dataset(
        LIGHT_JSON, emoji_test, annotations, unicode_version, full=False
    )
    light_size = write_dataset(LIGHT_JSON, light)
    print(f"  -> {light_size / 1024:.1f} KB")  # noqa: T201

    print(f"\nEnriching full dataset: {FULL_JSON.relative_to(REPO_ROOT)}")  # noqa: T201
    full = enrich_dataset(
        FULL_JSON, emoji_test, annotations, unicode_version, full=True
    )
    full_size = write_dataset(FULL_JSON, full)
    print(f"  -> {full_size / 1024:.1f} KB")  # noqa: T201


if __name__ == "__main__":
    main()
