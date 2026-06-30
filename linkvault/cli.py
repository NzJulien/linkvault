"""Command-line interface for linkvault.

Usage:
    linkvault add https://example.com -t "Example" --tags ref,docs
    linkvault list
    linkvault list --tag docs
    linkvault search "machine learning"
    linkvault tag <id> add python
    linkvault tag <id> remove python
    linkvault open <id>
    linkvault remove <id>
    linkvault tags
    linkvault check
    linkvault export bookmarks.md
    linkvault export bookmarks.html --format html
"""
from __future__ import annotations

import argparse
import sys
import webbrowser

from .checker import check_links
from .export import export_html, export_markdown
from .vault import Bookmark, LinkVault


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}"


def print_bookmark(b: Bookmark) -> None:
    tags = " ".join(f"#{t}" for t in b.tags)
    print(f"  {c('[' + b.id + ']', Color.BLUE)} {c(b.title, Color.BOLD)}")
    print(f"      {b.url}")
    if b.note:
        print(f"      {c(b.note, Color.YELLOW)}")
    meta = []
    if tags:
        meta.append(tags)
    if b.visits:
        meta.append(f"visited {b.visits}x")
    if meta:
        print(f"      {c(' · '.join(meta), Color.GREEN)}")


def cmd_add(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    tags = [t for t in (args.tags or "").split(",") if t.strip()]
    try:
        bookmark = vault.add(args.url, args.title or "", tags, args.note or "")
    except ValueError as exc:
        print(c(f"Error: {exc}", Color.RED))
        return 1
    print(c(f"Saved [{bookmark.id}] {bookmark.title}", Color.GREEN))
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    if vault.remove(args.id):
        print(c(f"Removed bookmark {args.id}", Color.GREEN))
        return 0
    print(c(f"No bookmark found with id {args.id}", Color.RED))
    return 1


def cmd_list(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    bookmarks = vault.bookmarks

    if args.tag:
        bookmarks = vault.by_tag(args.tag)
    if args.domain:
        bookmarks = [b for b in bookmarks if args.domain.lower() in b.domain.lower()]

    if not bookmarks:
        print(c("No bookmarks found.", Color.YELLOW))
        return 0

    bookmarks = sorted(bookmarks, key=lambda b: b.added_at, reverse=True)
    print(c(f"\n{len(bookmarks)} bookmark(s):\n", Color.BOLD))
    for b in bookmarks:
        print_bookmark(b)
        print()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    results = vault.search(args.query)
    if not results:
        print(c(f"No results for '{args.query}'.", Color.YELLOW))
        return 0
    print(c(f"\n{len(results)} result(s) for '{args.query}':\n", Color.BOLD))
    for b in results:
        print_bookmark(b)
        print()
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    tags = vault.all_tags()
    if not tags:
        print(c("No tags yet.", Color.YELLOW))
        return 0
    print(c("\nTags:\n", Color.BOLD))
    for tag, count in tags.items():
        print(f"  #{tag:<20} {count}")
    return 0


def cmd_tag(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    if args.action == "add":
        ok = vault.add_tag(args.id, args.tag)
    else:
        ok = vault.remove_tag(args.id, args.tag)
    if not ok:
        print(c(f"No bookmark found with id {args.id}", Color.RED))
        return 1
    print(c(f"{'Added' if args.action=='add' else 'Removed'} tag '{args.tag}' on {args.id}", Color.GREEN))
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    bookmark = vault.visit(args.id)
    if not bookmark:
        print(c(f"No bookmark found with id {args.id}", Color.RED))
        return 1
    print(f"Opening {bookmark.url} ...")
    webbrowser.open(bookmark.url)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    if not vault.bookmarks:
        print(c("No bookmarks to check.", Color.YELLOW))
        return 0
    print(f"Checking {len(vault.bookmarks)} link(s)...")
    results = check_links(vault.bookmarks)
    exit_code = 0
    for r in results:
        bookmark = vault.find(r.bookmark_id)
        title = bookmark.title if bookmark else r.url
        color = Color.GREEN if r.ok else Color.RED
        print(f"  {c(r.label, color):<22} {title} ({r.url})")
        if not r.ok:
            exit_code = 1
    return exit_code


def cmd_export(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    if not vault.bookmarks:
        print(c("Nothing to export.", Color.YELLOW))
        return 0
    if args.format == "html":
        export_html(vault.bookmarks, args.output)
    else:
        export_markdown(vault.bookmarks, args.output)
    print(c(f"Exported {len(vault.bookmarks)} bookmarks to {args.output}", Color.GREEN))
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    vault = LinkVault(args.storage)
    print(c("\nLinkVault stats", Color.BOLD))
    print("=" * 30)
    print(f"Total bookmarks: {len(vault.bookmarks)}")
    print(f"Unique tags:     {len(vault.all_tags())}")
    print(f"Unique domains:  {len(vault.all_domains())}")
    untagged = vault.untagged()
    if untagged:
        print(c(f"Untagged:        {len(untagged)}", Color.YELLOW))

    top_domains = list(vault.all_domains().items())[:5]
    if top_domains:
        print(c("\nTop domains:", Color.BLUE))
        for domain, count in top_domains:
            print(f"  {domain:<30} {count}")

    most_visited = vault.most_visited(5)
    if most_visited and most_visited[0].visits > 0:
        print(c("\nMost visited:", Color.BLUE))
        for b in most_visited:
            if b.visits:
                print(f"  {b.title:<30} {b.visits} visits")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="linkvault", description="A CLI bookmark manager with tags and dead-link checking.")
    parser.add_argument("--storage", default="bookmarks.json", help="Path to bookmarks JSON file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Save a new bookmark")
    p_add.add_argument("url")
    p_add.add_argument("-t", "--title", help="Title (default: page domain)")
    p_add.add_argument("--tags", help="Comma-separated tags")
    p_add.add_argument("-n", "--note", help="Optional note")
    p_add.set_defaults(func=cmd_add)

    p_remove = sub.add_parser("remove", help="Remove a bookmark by id")
    p_remove.add_argument("id")
    p_remove.set_defaults(func=cmd_remove)

    p_list = sub.add_parser("list", help="List bookmarks")
    p_list.add_argument("--tag", help="Filter by tag")
    p_list.add_argument("--domain", help="Filter by domain substring")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Full-text search across title, url, note, and tags")
    p_search.add_argument("query")
    p_search.set_defaults(func=cmd_search)

    p_tags = sub.add_parser("tags", help="List all tags with usage counts")
    p_tags.set_defaults(func=cmd_tags)

    p_tag = sub.add_parser("tag", help="Add or remove a tag on a bookmark")
    p_tag.add_argument("id")
    p_tag.add_argument("action", choices=["add", "remove"])
    p_tag.add_argument("tag")
    p_tag.set_defaults(func=cmd_tag)

    p_open = sub.add_parser("open", help="Open a bookmark in the browser and record a visit")
    p_open.add_argument("id")
    p_open.set_defaults(func=cmd_open)

    p_check = sub.add_parser("check", help="Check all bookmarks for dead links")
    p_check.set_defaults(func=cmd_check)

    p_export = sub.add_parser("export", help="Export bookmarks")
    p_export.add_argument("output")
    p_export.add_argument("--format", choices=["md", "html"], default="md")
    p_export.set_defaults(func=cmd_export)

    p_stats = sub.add_parser("stats", help="Show vault statistics")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
