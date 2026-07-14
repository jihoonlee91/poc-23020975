import json

import app


def use_temp_data_file(monkeypatch, tmp_path):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(app, "DATA_FILE", str(data_file))
    return data_file


def test_load_returns_empty_list_when_file_missing(monkeypatch, tmp_path):
    use_temp_data_file(monkeypatch, tmp_path)

    assert app.load() == []


def test_save_then_load_roundtrip(monkeypatch, tmp_path):
    use_temp_data_file(monkeypatch, tmp_path)

    items = [{"id": 1, "name": "apple", "value": "100"}]
    app.save(items)

    assert app.load() == items


def test_next_id_starts_at_1_when_empty():
    assert app.next_id([]) == 1


def test_next_id_is_max_plus_1():
    items = [{"id": 1}, {"id": 5}, {"id": 3}]

    assert app.next_id(items) == 6


def test_find_returns_matching_item():
    items = [{"id": 1, "name": "apple"}, {"id": 2, "name": "banana"}]

    assert app.find(items, 2) == {"id": 2, "name": "banana"}


def test_find_returns_none_when_not_found():
    items = [{"id": 1, "name": "apple"}]

    assert app.find(items, 999) is None


def test_create_appends_item_and_saves(monkeypatch, tmp_path):
    data_file = use_temp_data_file(monkeypatch, tmp_path)
    items = []
    inputs = iter(["apple", "100"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    app.create(items)

    assert items == [{"id": 1, "name": "apple", "value": "100"}]
    assert json.loads(data_file.read_text(encoding="utf-8")) == items


def test_update_changes_field_and_saves(monkeypatch, tmp_path):
    data_file = use_temp_data_file(monkeypatch, tmp_path)
    items = [{"id": 1, "name": "apple", "value": "100"}]
    inputs = iter(["1", "value", "999"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    app.update(items)

    assert items[0]["value"] == "999"
    assert json.loads(data_file.read_text(encoding="utf-8"))[0]["value"] == "999"


def test_update_rejects_unknown_field(monkeypatch, tmp_path, capsys):
    use_temp_data_file(monkeypatch, tmp_path)
    items = [{"id": 1, "name": "apple", "value": "100"}]
    inputs = iter(["1", "unknown_field"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    app.update(items)

    assert items[0]["value"] == "100"
    assert "ERROR" in capsys.readouterr().out


def test_update_rejects_non_numeric_id(monkeypatch, tmp_path, capsys):
    use_temp_data_file(monkeypatch, tmp_path)
    items = [{"id": 1, "name": "apple", "value": "100"}]
    monkeypatch.setattr("builtins.input", lambda *_: "abc")

    app.update(items)

    assert items[0]["value"] == "100"
    assert "ERROR" in capsys.readouterr().out


def test_delete_removes_item_when_confirmed(monkeypatch, tmp_path):
    data_file = use_temp_data_file(monkeypatch, tmp_path)
    items = [{"id": 1, "name": "apple", "value": "100"}]
    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    app.delete(items)

    assert items == []
    assert json.loads(data_file.read_text(encoding="utf-8")) == []


def test_delete_keeps_item_when_not_confirmed(monkeypatch, tmp_path):
    use_temp_data_file(monkeypatch, tmp_path)
    items = [{"id": 1, "name": "apple", "value": "100"}]
    inputs = iter(["1", "n"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    app.delete(items)

    assert items == [{"id": 1, "name": "apple", "value": "100"}]


def test_delete_reports_missing_id(monkeypatch, tmp_path, capsys):
    use_temp_data_file(monkeypatch, tmp_path)
    items = [{"id": 1, "name": "apple", "value": "100"}]
    monkeypatch.setattr("builtins.input", lambda *_: "999")

    app.delete(items)

    assert items == [{"id": 1, "name": "apple", "value": "100"}]
    assert "없습니다" in capsys.readouterr().out
