"""Regenerate the bundled emoji datasets from vendored CLDR sources.

Pure transform. Never accesses the network: the CLDR source files at
``third_party/cldr/`` are refreshed separately by the ``refresh-dataset``
GitHub workflow.

Inputs:
  third_party/cldr/emoji-test.txt   — canonical Unicode emoji list (UTS #51)
  third_party/cldr/en.xml           — CLDR English keyword annotations

Outputs:
  src/pymojis/infrastructure/data/emoji_data.json                                  (light)
  packages/pymojis-fulldata/src/pymojis_fulldata/data/full_emoji_data.json         (full)

Both files are overwritten in place. The script is idempotent: regenerating
on top of its own output yields byte-identical bytes (sorted CLDR order).

Run via ``make data``.
"""

import json
import re
import xml.etree.ElementTree as ET  # noqa: S405  vendored CLDR data, trusted input
from pathlib import Path
from typing import Any

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

# Fitzpatrick skin-tone modifier codepoints. Records containing any of these
# are excluded from the light dataset (variants live only in the full one).
SKIN_TONES = frozenset({"1F3FB", "1F3FC", "1F3FD", "1F3FE", "1F3FF"})

# Qualifications kept in the output. ``minimally-qualified`` (ZWJ sequences
# missing an internal FE0F selector) is excluded because every such record
# has a fully-qualified twin that is the canonical form.
KEPT_QUALIFICATIONS = frozenset({"fully-qualified", "unqualified", "component"})

# Closed set of top-level groups expected in emoji-test.txt. Mirrors the
# ``Categories`` Literal in src/pymojis/domain/entities/emojis.py; any drift
# (CLDR adds/renames a group) must be reflected there too.
EXPECTED_GROUPS = frozenset(
    {
        "Smileys & Emotion",
        "People & Body",
        "Component",
        "Animals & Nature",
        "Food & Drink",
        "Travel & Places",
        "Activities",
        "Objects",
        "Symbols",
        "Flags",
    }
)

# Matches a data line in emoji-test.txt, e.g.:
#   1F600                                                  ; fully-qualified     # 😀 E1.0 grinning face
_EMOJI_TEST_LINE = re.compile(
    r"^([0-9A-F ]+);\s*([\w-]+)\s*#\s*(\S+)\s+E(\d+\.\d+)\s+(.+)$",
    re.IGNORECASE,
)

# Matches the "# Version: X.Y" header inside emoji-test.txt.
_EMOJI_TEST_VERSION = re.compile(r"^#\s*Version:\s*(\d+\.\d+)", re.MULTILINE)

_GROUP_LINE = re.compile(r"^#\s*group:\s*(.+?)\s*$")
_SUBGROUP_LINE = re.compile(r"^#\s*subgroup:\s*(.+?)\s*$")

# GitHub-style shortcode derivation: lowercase, strip punctuation, collapse
# whitespace/dashes to underscores. Matches GitHub's convention for ~90% of
# emojis; an exact-parity shortcode list can be vendored in a future refresh.
_SHORTCODE_STRIP = re.compile(r"[^a-z0-9_\s-]")
_SHORTCODE_SEP = re.compile(r"[\s\-:,]+")


def parse_unicode_version(emoji_test_path: Path) -> str:
    content = emoji_test_path.read_text(encoding="utf-8")
    m = _EMOJI_TEST_VERSION.search(content)
    if not m:
        raise ValueError(f"Could not parse '# Version:' header from {emoji_test_path}")
    return m.group(1)


def parse_emoji_test(
    path: Path,
) -> list[tuple[str, str, dict[str, Any]]]:
    """Parse emoji-test.txt into a flat ordered list of (group, subgroup, record).

    Order follows the file (CLDR display order, not codepoint order).
    Records keep their original ``qualification`` label; downstream filtering
    decides which to drop.
    """
    out: list[tuple[str, str, dict[str, Any]]] = []
    current_group: str | None = None
    current_subgroup: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("#"):
            gm = _GROUP_LINE.match(line)
            if gm:
                current_group = gm.group(1)
                current_subgroup = None
                continue
            sm = _SUBGROUP_LINE.match(line)
            if sm:
                current_subgroup = sm.group(1)
            continue

        m = _EMOJI_TEST_LINE.match(line)
        if not m:
            continue
        if current_group is None or current_subgroup is None:
            raise ValueError(f"emoji record before any group/subgroup header: {line!r}")

        codes_str, qualification, emoji_char, version, name = m.groups()
        codes = codes_str.strip().upper().split()
        record = {
            "code": codes,
            "emoji": emoji_char,
            "name": name.strip(),
            "unicode_version": version,
            "qualification": qualification,
            "base_code": derive_base_code(codes),
        }
        out.append((current_group, current_subgroup, record))

    return out


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

    Returns ``None`` when the emoji has no skin-tone variant (already a base
    form), or when stripping leaves an empty sequence (the skin-tone modifier
    itself is its own record in the Component category).
    """
    if not any(c in SKIN_TONES for c in code):
        return None
    stripped = [c for c in code if c not in SKIN_TONES]
    return stripped or None


def derive_shortcode(name: str) -> str:
    s = name.lower()
    s = _SHORTCODE_STRIP.sub("", s)
    s = _SHORTCODE_SEP.sub("_", s).strip("_")
    return f":{s}:"


def enrich_full(record: dict[str, Any], annotations: dict[str, list[str]]) -> None:
    record["keywords"] = annotations.get(record["emoji"], [])
    record["shortcodes"] = {"github": derive_shortcode(record["name"])}


def build_dataset(
    entries: list[tuple[str, str, dict[str, Any]]],
    annotations: dict[str, list[str]],
    *,
    full: bool,
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Group entries into ``category -> subcategory -> [record]`` shape.

    Applies the qualification filter for both datasets and the skin-tone
    filter for light. Records preserve emoji-test.txt order within each
    subgroup.
    """
    nested: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for group, subgroup, record in entries:
        if record["qualification"] not in KEPT_QUALIFICATIONS:
            continue
        if not full and any(c in SKIN_TONES for c in record["code"]):
            continue
        if group not in EXPECTED_GROUPS:
            raise ValueError(
                f"Unexpected CLDR group {group!r} — update EXPECTED_GROUPS "
                f"and the Categories Literal in domain/entities/emojis.py."
            )
        out_record = dict(record)
        if full:
            enrich_full(out_record, annotations)
        nested.setdefault(group, {}).setdefault(subgroup, []).append(out_record)
    return nested


def write_dataset(path: Path, unicode_version: str, emojis: dict[str, Any]) -> int:
    payload = {
        "@version": unicode_version,
        "@source": (
            "Unicode CLDR — emoji-test.txt + annotations/en.xml "
            "(vendored under third_party/cldr/)"
        ),
        "@cldr": f"Unicode {unicode_version} (vendored CLDR annotations)",
        "emojis": emojis,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path.stat().st_size


def main() -> None:
    print(f"Reading CLDR sources from {CLDR_DIR}")  # noqa: T201
    unicode_version = parse_unicode_version(EMOJI_TEST)
    print(f"  unicode version: {unicode_version}")  # noqa: T201

    entries = parse_emoji_test(EMOJI_TEST)
    print(f"  emoji-test.txt:  {len(entries)} raw records")  # noqa: T201

    annotations = parse_annotations(ANNOTATIONS_XML)
    print(f"  annotations:     {len(annotations)} records")  # noqa: T201

    print(f"\nBuilding light dataset: {LIGHT_JSON.relative_to(REPO_ROOT)}")  # noqa: T201
    light = build_dataset(entries, annotations, full=False)
    light_count = sum(len(recs) for subs in light.values() for recs in subs.values())
    light_size = write_dataset(LIGHT_JSON, unicode_version, light)
    print(f"  -> {light_count} records, {light_size / 1024:.1f} KB")  # noqa: T201

    print(f"\nBuilding full dataset:  {FULL_JSON.relative_to(REPO_ROOT)}")  # noqa: T201
    full = build_dataset(entries, annotations, full=True)
    full_count = sum(len(recs) for subs in full.values() for recs in subs.values())
    full_size = write_dataset(FULL_JSON, unicode_version, full)
    print(f"  -> {full_count} records, {full_size / 1024:.1f} KB")  # noqa: T201


if __name__ == "__main__":
    main()
