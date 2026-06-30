"""Export bookmarks to Markdown or the standard Netscape Bookmark HTML format
(importable by every major browser)."""
from __future__ import annotations

from pathlib import Path

from .vault import Bookmark


def export_markdown(bookmarks: list[Bookmark], path: str | Path) -> None:
    path = Path(path)
    by_tag: dict[str, list[Bookmark]] = {}
    untagged: list[Bookmark] = []

    for b in bookmarks:
        if not b.tags:
            untagged.append(b)
        for tag in b.tags:
            by_tag.setdefault(tag, []).append(b)

    lines = ["# Bookmarks", ""]
    for tag in sorted(by_tag):
        lines.append(f"## {tag}")
        for b in sorted(by_tag[tag], key=lambda x: x.title.lower()):
            note = f" — {b.note}" if b.note else ""
            lines.append(f"- [{b.title}]({b.url}){note}")
        lines.append("")

    if untagged:
        lines.append("## untagged")
        for b in sorted(untagged, key=lambda x: x.title.lower()):
            note = f" — {b.note}" if b.note else ""
            lines.append(f"- [{b.title}]({b.url}){note}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def export_html(bookmarks: list[Bookmark], path: str | Path) -> None:
    """Write the Netscape Bookmark File Format, importable by Chrome/Firefox/Safari."""
    path = Path(path)
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
    ]
    for b in sorted(bookmarks, key=lambda x: x.title.lower()):
        tags_attr = f' TAGS="{",".join(b.tags)}"' if b.tags else ""
        lines.append(f'    <DT><A HREF="{b.url}"{tags_attr}>{_escape(b.title)}</A>')
        if b.note:
            lines.append(f"    <DD>{_escape(b.note)}")
    lines.append("</DL><p>")
    path.write_text("\n".join(lines), encoding="utf-8")


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
