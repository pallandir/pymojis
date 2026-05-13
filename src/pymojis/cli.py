import argparse
import sys

from pymojis.application.pymojis_manager import PymojisManager
from pymojis.domain.entities.emojis import Emoji


def _format_emoji_line(emoji: Emoji) -> str:
    return f"{emoji.emoji}  {emoji.name}  ({emoji.category} / {emoji.sub_category})"


def _cmd_search(args: argparse.Namespace) -> int:
    manager = PymojisManager(use_full_dataset=args.full)
    results = manager.search(args.query, limit=args.limit)
    if not results:
        print(f"No matches for {args.query!r}", file=sys.stderr)
        return 1
    for e in results:
        print(_format_emoji_line(e))
    return 0


def _cmd_random(args: argparse.Namespace) -> int:
    manager = PymojisManager(use_full_dataset=args.full)
    exclude = args.exclude if args.exclude else None
    emojis = manager.get_random(length=args.length, exclude=exclude)
    for e in emojis:
        print(_format_emoji_line(e) if args.verbose else e.emoji)
    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    manager = PymojisManager(use_full_dataset=args.full)
    record = manager.get_by_emoji(args.emoji)
    if record is None:
        print(f"Unknown emoji: {args.emoji!r}", file=sys.stderr)
        return 1
    print(f"emoji:           {record.emoji}")
    print(f"name:            {record.name}")
    print(f"code:            {' '.join(record.code)}")
    print(f"category:        {record.category}")
    print(f"sub_category:    {record.sub_category}")
    print(f"unicode_version: {record.unicode_version}")
    print(f"qualification:   {record.qualification}")
    if record.base_code:
        print(f"base_code:       {' '.join(record.base_code)}")
    if record.keywords:
        print(f"keywords:        {', '.join(record.keywords)}")
    for set_name, code in record.shortcodes.items():
        print(f"shortcode[{set_name}]: {code}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pymojis",
        description="Search and inspect emojis from the command line.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use the full dataset (requires `pip install 'pymojis[full]'`).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("search", help="Find emojis by name or keyword.")
    sp.add_argument("query", help="Search term.")
    sp.add_argument("--limit", type=int, default=10, help="Max results (default: 10).")

    sp = subparsers.add_parser("random", help="Print random emojis.")
    sp.add_argument(
        "--length", type=int, default=1, help="Number of emojis (default: 1)."
    )
    sp.add_argument(
        "--exclude",
        choices=["complex"],
        default=None,
        help="`complex` excludes multi-codepoint emojis.",
    )
    sp.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print full record per line instead of just the glyph.",
    )

    sp = subparsers.add_parser("info", help="Print all known details for an emoji.")
    sp.add_argument("emoji", help="The emoji character (e.g. '😀').")

    return parser


_COMMANDS = {
    "search": _cmd_search,
    "random": _cmd_random,
    "info": _cmd_info,
}


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    handler = _COMMANDS[args.command]
    return handler(args)
