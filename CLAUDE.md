# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This repo has two layers, deliberately kept separate:

- **`poc.py`** — a quick, unpolished PoC ("does JSON-file-as-storage work at all?") built with vibe coding. It's a historical artifact demonstrating the validated approach — **do not "clean up" or refactor it**; if it needs to change, that means the PoC assumption was wrong and should be re-validated, not silently patched.
- **`app.py`** — the real CRUD console app, built by carrying over `poc.py`'s structure (`load`/`save`/`find`) into an actual interactive tool. This is the one that gets maintained, tested, and improved going forward.

`IMPROVEMENTS.md` documents issues found during a later review pass of `app.py` (atomic saves, corrupted-file handling, input validation) and how they were fixed — read it before assuming something in `app.py` is still a rough PoC-era shortcut.

## Commands

```
python app.py                 # run the CRUD console app (data persisted to data.json)
pip install pytest
pytest tests                  # run all tests
pytest tests/test_app.py -v   # run with verbose per-test output
```

`tests/conftest.py` adds the repo root to `sys.path` so `tests/test_app.py` can do `import app` directly (no package/`__init__.py` involved). Run pytest from the repo root, or reference `tests` explicitly.

## Architecture (`app.py`)

Everything operates on a single in-memory list of dict records (`{"id": int, "name": str, "value": str}`), persisted to `data.json`:

- `load()` / `save(items)` — the only file I/O. `save()` writes to a temp file in the same directory and `os.replace()`s it into place (atomic — a crash mid-write can't corrupt `data.json`). `load()` swallows `JSONDecodeError` on a corrupted file, warns, and returns `[]` rather than crashing.
- `next_id(items)` / `find(items, item_id)` — pure helpers, no I/O.
- `_prompt_item_id(prompt)` — shared "read an int ID from input, print an error and return `None` on bad input" used by both `update()` and `delete()`. Any new command needing an ID input should reuse this rather than re-inlining the try/except.
- `create` / `read_all` / `read_one` / `update` / `delete` — each does its own `input()`/`print()` directly (no I/O abstraction layer like the `Assemble`/`AssembleConsole` split seen in other repos — this app is small enough that testing via `monkeypatch.setattr("builtins.input", ...)` + `capsys` is sufficient, see `tests/test_app.py`).
- `main()` — a menu loop dispatching on the user's numeric choice; `0` exits.

When adding a new field to a record or a new menu action, follow the existing pattern: pure logic stays testable without real stdin/files (tests monkeypatch `app.DATA_FILE` to a `tmp_path` and `builtins.input` to a canned iterator), and any new "must exist" or "must be well-formed" input check should short-circuit with an `ERROR ::`-prefixed message rather than raising.
