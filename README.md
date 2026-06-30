# linkvault

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-31%20passing-brightgreen)

**A CLI bookmark manager — tags, full-text search, dead-link checking, and export to Markdown or browser-importable HTML. Zero runtime dependencies.**

## Why

Browser bookmark bars get messy fast, and most bookmark services want a
sign-up and a subscription. `linkvault` is a single JSON file on your own
disk, a fast CLI, and just enough structure (tags, notes, search) to
actually find things again.

## Install

```bash
git clone https://github.com/NzJulien/linkvault.git
cd linkvault
pip install -e .
```

## Quick start

```bash
linkvault add python.org -t "Python" --tags lang,docs
linkvault add github.com/anthropics --tags ai,code -n "Anthropic's repos"

linkvault list
linkvault list --tag docs
linkvault search "python"
```

```
2 bookmark(s):

  [d43f002b] Anthropic on GitHub
      https://github.com/anthropics
      Anthropic's repos
      #ai #code

  [bab8c1ad] Python
      https://python.org
      #docs #lang
```

## Tagging

```bash
linkvault tag bab8c1ad add favorites
linkvault tag bab8c1ad remove lang
linkvault tags          # see every tag with a usage count
```

## Dead-link checking

```bash
linkvault check
```

```
Checking 3 link(s)...
  OK (200)              Python (https://python.org)
  FAILED (404)          Old Blog Post (https://example.com/gone)
  ERROR (Name or...)    Typo Domain (https://exmaple.com)
```

Exits with status `1` if any link failed — useful in a periodic cleanup script.

## Export

```bash
linkvault export bookmarks.md                 # Markdown, grouped by tag
linkvault export bookmarks.html --format html  # Netscape format — import into any browser
```

## All commands

| Command | Description |
|---|---|
| `add <url> [-t title] [--tags a,b] [-n note]` | Save a new bookmark |
| `remove <id>` | Delete a bookmark |
| `list [--tag X] [--domain Y]` | List bookmarks, optionally filtered |
| `search <query>` | Full-text search across title, url, note, tags |
| `tags` | List every tag with a usage count |
| `tag <id> add\|remove <tag>` | Add or remove a tag from a bookmark |
| `open <id>` | Open in the default browser, records a visit |
| `check` | Check every bookmark for dead links |
| `export <file> [--format md\|html]` | Export bookmarks |
| `stats` | Summary: totals, top domains, most visited |

## Library usage

```python
from linkvault import LinkVault, check_links

vault = LinkVault("bookmarks.json")
vault.add("python.org", "Python", tags=["lang"])

print(vault.search("python"))
print(vault.all_tags())          # {'lang': 1}

results = check_links(vault.bookmarks)
for r in results:
    print(r.url, r.label)
```

## Project layout

```
linkvault/
├── linkvault/
│   ├── vault.py        # Bookmark dataclass + LinkVault (storage & queries)
│   ├── checker.py       # Dead-link checking, network isolated behind one function
│   ├── export.py        # Markdown + Netscape HTML export
│   └── cli.py            # argparse CLI: add, remove, list, search, tag, check, export, stats
├── tests/                # pytest suite (31 tests)
├── setup.py
└── LICENSE
```

## Running the tests

The dead-link checker's network call is isolated behind a single
`fetch_status` function, so `check_links` is fully testable with a fake
fetcher — the test suite makes zero real HTTP requests.

```bash
pip install -e ".[dev]"
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).

---

Made by [NzJulien](https://github.com/NzJulien)
