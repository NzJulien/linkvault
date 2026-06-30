"""Check bookmarks for dead or redirected links.

Network access is isolated behind a single ``fetch_status`` function so the
checking logic itself (``check_links``) can be fully unit tested by
injecting a fake fetcher — no real HTTP calls needed in tests.
"""
from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Optional

from .vault import Bookmark


@dataclass
class LinkStatus:
    bookmark_id: str
    url: str
    ok: bool
    status_code: Optional[int]
    error: Optional[str] = None

    @property
    def label(self) -> str:
        if self.ok:
            return f"OK ({self.status_code})"
        if self.status_code:
            return f"FAILED ({self.status_code})"
        return f"ERROR ({self.error})"


def fetch_status(url: str, timeout: float = 5.0) -> tuple[Optional[int], Optional[str]]:
    """Perform a real HTTP request and return (status_code, error_message)."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "linkvault/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except urllib.error.URLError as exc:
        return None, str(exc.reason)
    except Exception as exc:  # noqa: BLE001 - surface any unexpected failure as a status
        return None, str(exc)


def check_links(
    bookmarks: list[Bookmark],
    fetcher: Callable[[str], tuple[Optional[int], Optional[str]]] = fetch_status,
) -> list[LinkStatus]:
    """Check each bookmark's URL using ``fetcher`` and report its status.

    ``fetcher`` takes a URL and returns ``(status_code, error_message)``,
    exactly one of which should be set. A bookmark is considered OK when
    the status code is in the 200-399 range.
    """
    results = []
    for b in bookmarks:
        status_code, error = fetcher(b.url)
        ok = status_code is not None and 200 <= status_code < 400
        results.append(LinkStatus(bookmark_id=b.id, url=b.url, ok=ok, status_code=status_code, error=error))
    return results
