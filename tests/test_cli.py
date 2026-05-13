import pytest

from pymojis.cli import main


def test_search_known_query(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["search", "grinning"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "grinning" in captured.out.lower()


def test_search_no_results_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["search", "zzz_no_such_emoji_zzz"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No matches" in captured.err


def test_search_limit(capsys: pytest.CaptureFixture[str]) -> None:
    main(["search", "face", "--limit", "2"])
    captured = capsys.readouterr()
    # Each result is one line.
    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert len(lines) == 2


def test_random_default_one(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["random"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(captured.out.splitlines()) == 1


def test_random_length(capsys: pytest.CaptureFixture[str]) -> None:
    main(["random", "--length", "3"])
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 3


def test_random_verbose(capsys: pytest.CaptureFixture[str]) -> None:
    main(["random", "--length", "1", "-v"])
    captured = capsys.readouterr()
    line = captured.out.strip()
    # Verbose lines include name and category.
    assert "(" in line and "/" in line


def test_info_known_emoji(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["info", "😀"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "grinning face" in captured.out
    assert "1F600" in captured.out
    assert "Smileys & Emotion" in captured.out


def test_info_unknown_emoji_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["info", "z"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Unknown" in captured.err


def test_no_command_errors(capsys: pytest.CaptureFixture[str]) -> None:
    # argparse exits 2 on missing required subcommand.
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_unknown_command_errors() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["bogus"])
    assert excinfo.value.code == 2


def test_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
