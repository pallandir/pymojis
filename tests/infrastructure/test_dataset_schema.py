"""Schema-validation walk over the bundled dataset JSON.

Catches dataset regressions early: any record missing a v2 schema field, or
any field with the wrong type, fails CI before downstream code sees it.
"""

import json
from pathlib import Path
from typing import Any, get_args

import pytest

from pymojis.domain.entities.emojis import Categories, Qualification

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LIGHT_PATH = (
    _REPO_ROOT / "src" / "pymojis" / "infrastructure" / "data" / "emoji_data.json"
)
_FULL_PATH = (
    _REPO_ROOT
    / "packages"
    / "pymojis-fulldata"
    / "src"
    / "pymojis_fulldata"
    / "data"
    / "full_emoji_data.json"
)

_VALID_CATEGORIES = set(get_args(Categories))
_VALID_QUALIFICATIONS = set(get_args(Qualification))


def _validate_record(record: dict[str, Any], *, full: bool) -> None:
    for key, expected_type in (
        ("code", list),
        ("emoji", str),
        ("name", str),
        ("unicode_version", str),
        ("qualification", str),
    ):
        assert key in record, f"missing required field {key!r}: {record!r}"
        assert isinstance(record[key], expected_type), (
            f"field {key!r} has wrong type: {record!r}"
        )

    assert record["code"], f"code must be non-empty: {record!r}"
    assert all(isinstance(c, str) and c for c in record["code"]), (
        f"code must be list of non-empty strings: {record!r}"
    )
    assert record["qualification"] in _VALID_QUALIFICATIONS, (
        f"qualification not in {_VALID_QUALIFICATIONS}: {record!r}"
    )

    assert "base_code" in record, f"missing base_code (use null): {record!r}"
    if record["base_code"] is not None:
        assert isinstance(record["base_code"], list) and record["base_code"], (
            f"base_code must be null or non-empty list: {record!r}"
        )

    if full:
        assert "keywords" in record and isinstance(record["keywords"], list), (
            f"full schema requires keywords list: {record!r}"
        )
        assert "shortcodes" in record and isinstance(record["shortcodes"], dict), (
            f"full schema requires shortcodes dict: {record!r}"
        )
        assert "github" in record["shortcodes"], (
            f"full schema requires shortcodes.github: {record!r}"
        )


def _walk(path: Path, *, full: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "emojis" in data, f"{path} missing 'emojis' top-level key"
    assert isinstance(data["emojis"], dict)
    count = 0
    for category, subcats in data["emojis"].items():
        assert category in _VALID_CATEGORIES, f"unknown category: {category!r}"
        assert isinstance(subcats, dict)
        for subcat, records in subcats.items():
            assert isinstance(subcat, str) and subcat
            assert isinstance(records, list)
            for r in records:
                _validate_record(r, full=full)
                count += 1
    return count


def test_light_dataset_schema() -> None:
    count = _walk(_LIGHT_PATH, full=False)
    assert count > 0, "light dataset is empty"


def test_full_dataset_schema() -> None:
    if not _FULL_PATH.exists():
        pytest.skip("full dataset not present")
    count = _walk(_FULL_PATH, full=True)
    assert count > 0, "full dataset is empty"
