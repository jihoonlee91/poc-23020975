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


def test_load_returns_empty_list_and_warns_on_corrupted_file(monkeypatch, tmp_path, capsys):
    data_file = use_temp_data_file(monkeypatch, tmp_path)
    data_file.write_text("{이거는 잘못된 JSON", encoding="utf-8")

    items = app.load()

    assert items == []
    assert "ERROR" in capsys.readouterr().out


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


def test_read_all_prints_message_when_empty(capsys):
    app.read_all([])

    assert "데이터가 없습니다." in capsys.readouterr().out


def test_read_all_prints_every_item(capsys):
    items = [{"id": 1, "name": "apple"}, {"id": 2, "name": "banana"}]

    app.read_all(items)

    out = capsys.readouterr().out
    assert "apple" in out
    assert "banana" in out


def test_read_one_finds_by_id(monkeypatch, capsys):
    items = [{"id": 1, "name": "apple"}, {"id": 2, "name": "banana"}]
    monkeypatch.setattr("builtins.input", lambda *_: "2")

    app.read_one(items)

    assert "banana" in capsys.readouterr().out


def test_read_one_finds_by_name(monkeypatch, capsys):
    items = [{"id": 1, "name": "apple"}, {"id": 2, "name": "banana"}]
    monkeypatch.setattr("builtins.input", lambda *_: "apple")

    app.read_one(items)

    assert "apple" in capsys.readouterr().out


def test_read_one_reports_no_match(monkeypatch, capsys):
    items = [{"id": 1, "name": "apple"}]
    monkeypatch.setattr("builtins.input", lambda *_: "no-such-thing")

    app.read_one(items)

    assert "일치하는 데이터가 없습니다." in capsys.readouterr().out


def test_create_rejects_empty_name(monkeypatch, tmp_path, capsys):
    use_temp_data_file(monkeypatch, tmp_path)
    items = []
    monkeypatch.setattr("builtins.input", lambda *_: "")

    app.create(items)

    assert items == []
    assert "ERROR" in capsys.readouterr().out


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
