from linkvault.export import export_html, export_markdown
from linkvault.vault import Bookmark


def test_export_markdown_groups_by_tag(tmp_path):
    bookmarks = [
        Bookmark.create("a.com", "Article A", tags=["python"]),
        Bookmark.create("b.com", "Article B", tags=["python", "ai"]),
        Bookmark.create("c.com", "Article C"),  # untagged
    ]
    out = tmp_path / "out.md"
    export_markdown(bookmarks, out)
    content = out.read_text()

    assert "## python" in content
    assert "## ai" in content
    assert "## untagged" in content
    assert "[Article A](https://a.com)" in content
    assert "[Article C](https://c.com)" in content


def test_export_markdown_includes_notes(tmp_path):
    bookmarks = [Bookmark.create("a.com", "Article A", tags=["x"], note="great read")]
    out = tmp_path / "out.md"
    export_markdown(bookmarks, out)
    assert "great read" in out.read_text()


def test_export_html_is_valid_netscape_format(tmp_path):
    bookmarks = [Bookmark.create("a.com", "Article A", tags=["python"])]
    out = tmp_path / "out.html"
    export_html(bookmarks, out)
    content = out.read_text()

    assert "<!DOCTYPE NETSCAPE-Bookmark-file-1>" in content
    assert '<A HREF="https://a.com"' in content
    assert "Article A" in content


def test_export_html_escapes_special_characters(tmp_path):
    bookmarks = [Bookmark.create("a.com", "A & B <Test>")]
    out = tmp_path / "out.html"
    export_html(bookmarks, out)
    content = out.read_text()
    assert "&amp;" in content
    assert "&lt;Test&gt;" in content
