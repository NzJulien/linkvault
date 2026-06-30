import pytest
from linkvault.vault import Bookmark, LinkVault, domain_of


def test_create_bookmark_adds_scheme_if_missing():
    b = Bookmark.create("example.com")
    assert b.url == "https://example.com"


def test_create_bookmark_keeps_existing_scheme():
    b = Bookmark.create("http://example.com")
    assert b.url == "http://example.com"


def test_create_bookmark_rejects_empty_url():
    with pytest.raises(ValueError):
        Bookmark.create("   ")


def test_create_bookmark_defaults_title_to_domain():
    b = Bookmark.create("https://example.com/page")
    assert b.title == "example.com"


def test_create_bookmark_normalizes_tags():
    b = Bookmark.create("example.com", tags=["Python", "python", " AI ", ""])
    assert b.tags == ["ai", "python"]


def test_domain_of_strips_www():
    assert domain_of("https://www.example.com/page") == "example.com"
    assert domain_of("https://example.com") == "example.com"


def test_bookmark_round_trip_dict():
    b = Bookmark.create("example.com", "Example", ["ref"], "a note")
    restored = Bookmark.from_dict(b.to_dict())
    assert restored == b


def test_vault_add_and_persist(tmp_path):
    path = tmp_path / "b.json"
    vault = LinkVault(path)
    vault.add("example.com", "Example")
    vault.add("python.org", "Python")

    reloaded = LinkVault(path)
    assert len(reloaded.bookmarks) == 2


def test_vault_add_rejects_duplicate_url(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    vault.add("example.com")
    with pytest.raises(ValueError):
        vault.add("https://example.com/")  # trailing slash, should still match


def test_vault_remove(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    b = vault.add("example.com")
    assert vault.remove(b.id) is True
    assert vault.remove(b.id) is False
    assert len(vault.bookmarks) == 0


def test_vault_find_by_url(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    b = vault.add("example.com")
    assert vault.find_by_url("example.com") == b
    assert vault.find_by_url("https://example.com") == b


def test_vault_by_tag(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    vault.add("a.com", tags=["python"])
    vault.add("b.com", tags=["python", "ai"])
    vault.add("c.com", tags=["ai"])
    assert len(vault.by_tag("python")) == 2
    assert len(vault.by_tag("ai")) == 2


def test_vault_search_across_fields(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    vault.add("example.com", title="Cool Article", note="about rockets")
    vault.add("other.com", title="Boring Page")
    results = vault.search("rockets")
    assert len(results) == 1
    assert results[0].title == "Cool Article"


def test_vault_search_empty_query_returns_all(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    vault.add("a.com")
    vault.add("b.com")
    assert len(vault.search("")) == 2


def test_vault_visit_increments_count(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    b = vault.add("example.com")
    vault.visit(b.id)
    vault.visit(b.id)
    assert vault.find(b.id).visits == 2


def test_vault_add_and_remove_tag(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    b = vault.add("example.com")
    vault.add_tag(b.id, "Python")
    assert vault.find(b.id).tags == ["python"]
    vault.remove_tag(b.id, "python")
    assert vault.find(b.id).tags == []


def test_vault_all_tags_counts(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    vault.add("a.com", tags=["python"])
    vault.add("b.com", tags=["python", "ai"])
    tags = vault.all_tags()
    assert tags["python"] == 2
    assert tags["ai"] == 1


def test_vault_untagged(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    vault.add("a.com", tags=["python"])
    b2 = vault.add("b.com")
    untagged = vault.untagged()
    assert len(untagged) == 1
    assert untagged[0].id == b2.id


def test_vault_most_visited(tmp_path):
    vault = LinkVault(tmp_path / "b.json")
    a = vault.add("a.com")
    b = vault.add("b.com")
    vault.visit(b.id)
    vault.visit(b.id)
    vault.visit(a.id)
    most = vault.most_visited(2)
    assert most[0].id == b.id
