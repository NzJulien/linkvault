"""Core bookmark data model and storage/query logic."""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


@dataclass
class Bookmark:
    id: str
    url: str
    title: str
    tags: list[str] = field(default_factory=list)
    note: str = ""
    added_at: str = ""
    visits: int = 0

    @classmethod
    def create(cls, url: str, title: str = "", tags: Optional[list[str]] = None, note: str = "") -> "Bookmark":
        url = url.strip()
        if not url:
            raise ValueError("url cannot be empty")
        if not _URL_RE.match(url):
            url = "https://" + url

        normalized_tags = sorted({t.strip().lower() for t in (tags or []) if t.strip()})

        return cls(
            id=uuid.uuid4().hex[:8],
            url=url,
            title=title.strip() or domain_of(url),
            tags=normalized_tags,
            note=note.strip(),
            added_at=datetime.now().isoformat(timespec="seconds"),
            visits=0,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        return cls(**data)

    @property
    def domain(self) -> str:
        return domain_of(self.url)


def domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc[4:] if netloc.startswith("www.") else netloc
    except ValueError:
        return url


class LinkVault:
    """Loads, stores, and queries bookmarks persisted as a JSON file."""

    def __init__(self, storage_path: str | Path = "bookmarks.json"):
        self.storage_path = Path(storage_path)
        self.bookmarks: list[Bookmark] = []
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.bookmarks = [Bookmark.from_dict(b) for b in raw]
        else:
            self.bookmarks = []

    def save(self) -> None:
        data = [b.to_dict() for b in self.bookmarks]
        self.storage_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def add(self, url: str, title: str = "", tags: Optional[list[str]] = None, note: str = "") -> Bookmark:
        existing = self.find_by_url(url)
        if existing:
            raise ValueError(f"URL already saved as [{existing.id}] {existing.title}")
        bookmark = Bookmark.create(url, title, tags, note)
        self.bookmarks.append(bookmark)
        self.save()
        return bookmark

    def remove(self, bookmark_id: str) -> bool:
        before = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b.id != bookmark_id]
        removed = len(self.bookmarks) != before
        if removed:
            self.save()
        return removed

    def find(self, bookmark_id: str) -> Optional[Bookmark]:
        for b in self.bookmarks:
            if b.id == bookmark_id:
                return b
        return None

    def find_by_url(self, url: str) -> Optional[Bookmark]:
        normalized = url.strip()
        if not _URL_RE.match(normalized):
            normalized = "https://" + normalized
        for b in self.bookmarks:
            if b.url.rstrip("/") == normalized.rstrip("/"):
                return b
        return None

    def visit(self, bookmark_id: str) -> Optional[Bookmark]:
        bookmark = self.find(bookmark_id)
        if bookmark:
            bookmark.visits += 1
            self.save()
        return bookmark

    def add_tag(self, bookmark_id: str, tag: str) -> bool:
        bookmark = self.find(bookmark_id)
        if not bookmark:
            return False
        tag = tag.strip().lower()
        if tag and tag not in bookmark.tags:
            bookmark.tags = sorted(bookmark.tags + [tag])
            self.save()
        return True

    def remove_tag(self, bookmark_id: str, tag: str) -> bool:
        bookmark = self.find(bookmark_id)
        if not bookmark:
            return False
        tag = tag.strip().lower()
        if tag in bookmark.tags:
            bookmark.tags = [t for t in bookmark.tags if t != tag]
            self.save()
        return True

    # ---- Queries -----------------------------------------------------

    def by_tag(self, tag: str) -> list[Bookmark]:
        tag = tag.strip().lower()
        return [b for b in self.bookmarks if tag in b.tags]

    def by_domain(self, domain: str) -> list[Bookmark]:
        domain = domain.strip().lower()
        return [b for b in self.bookmarks if domain in b.domain.lower()]

    def search(self, query: str) -> list[Bookmark]:
        """Case-insensitive search across title, url, note, and tags."""
        q = query.strip().lower()
        if not q:
            return list(self.bookmarks)
        results = []
        for b in self.bookmarks:
            haystack = " ".join([b.title, b.url, b.note, " ".join(b.tags)]).lower()
            if q in haystack:
                results.append(b)
        return results

    def all_tags(self) -> dict[str, int]:
        """Tag -> count of bookmarks using it, sorted by frequency descending."""
        counts: dict[str, int] = {}
        for b in self.bookmarks:
            for t in b.tags:
                counts[t] = counts.get(t, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def all_domains(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for b in self.bookmarks:
            d = b.domain
            counts[d] = counts.get(d, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def most_visited(self, limit: int = 5) -> list[Bookmark]:
        return sorted(self.bookmarks, key=lambda b: -b.visits)[:limit]

    def untagged(self) -> list[Bookmark]:
        return [b for b in self.bookmarks if not b.tags]
