from linkvault.checker import check_links, LinkStatus
from linkvault.vault import Bookmark


def make_fake_fetcher(mapping):
    """mapping: url -> (status_code, error) so tests never hit the real network."""
    def fetcher(url):
        return mapping.get(url, (None, "not found in fake mapping"))
    return fetcher


def test_check_links_all_ok():
    bookmarks = [Bookmark.create("a.com"), Bookmark.create("b.com")]
    fetcher = make_fake_fetcher({
        "https://a.com": (200, None),
        "https://b.com": (301, None),
    })
    results = check_links(bookmarks, fetcher)
    assert all(r.ok for r in results)


def test_check_links_detects_failure():
    bookmarks = [Bookmark.create("dead.com")]
    fetcher = make_fake_fetcher({"https://dead.com": (404, None)})
    results = check_links(bookmarks, fetcher)
    assert results[0].ok is False
    assert results[0].status_code == 404


def test_check_links_detects_connection_error():
    bookmarks = [Bookmark.create("unreachable.com")]
    fetcher = make_fake_fetcher({"https://unreachable.com": (None, "Name or service not known")})
    results = check_links(bookmarks, fetcher)
    assert results[0].ok is False
    assert results[0].status_code is None
    assert "not known" in results[0].error


def test_check_links_500_is_failure():
    bookmarks = [Bookmark.create("broken.com")]
    fetcher = make_fake_fetcher({"https://broken.com": (500, None)})
    results = check_links(bookmarks, fetcher)
    assert results[0].ok is False


def test_link_status_label_ok():
    status = LinkStatus(bookmark_id="x", url="https://a.com", ok=True, status_code=200)
    assert status.label == "OK (200)"


def test_link_status_label_failed():
    status = LinkStatus(bookmark_id="x", url="https://a.com", ok=False, status_code=404)
    assert status.label == "FAILED (404)"


def test_link_status_label_error():
    status = LinkStatus(bookmark_id="x", url="https://a.com", ok=False, status_code=None, error="timeout")
    assert status.label == "ERROR (timeout)"


def test_check_links_preserves_order():
    bookmarks = [Bookmark.create(f"site{i}.com") for i in range(5)]
    fetcher = make_fake_fetcher({b.url: (200, None) for b in bookmarks})
    results = check_links(bookmarks, fetcher)
    assert [r.bookmark_id for r in results] == [b.id for b in bookmarks]
