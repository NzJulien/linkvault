from linkvault.cli import main


def test_corrupt_storage_file_is_clean_error(tmp_path, capsys):
    bad = tmp_path / "bookmarks.json"
    bad.write_text("{not json", encoding="utf-8")
    assert main(["--storage", str(bad), "list"]) == 1
    out = capsys.readouterr().out
    assert "bookmarks.json" in out
    assert "Traceback" not in out


def test_list_empty_storage_is_clean(tmp_path, capsys):
    assert main(["--storage", str(tmp_path / "bookmarks.json"), "list"]) == 0
    assert "No bookmarks found." in capsys.readouterr().out
