"""linkvault — a small, dependency-free CLI bookmark manager.

Save URLs with tags and notes, search them full-text, organize by tag,
and check for dead links — all backed by a single JSON file.
"""
from .vault import Bookmark, LinkVault
from .checker import check_links, LinkStatus

__version__ = "1.0.0"
__all__ = ["Bookmark", "LinkVault", "check_links", "LinkStatus"]
