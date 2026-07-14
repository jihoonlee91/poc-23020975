import json
import os

DATA_FILE = "data.json"


def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def next_id(items):
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def add(items, name, value):
    item = {"id": next_id(items), "name": name, "value": value}
    items.append(item)
    save(items)
    return item


def find(items, item_id):
    return next((item for item in items if item["id"] == item_id), None)


def update(items, item_id, **fields):
    item = find(items, item_id)
    if item is None:
        return None
    item.update(fields)
    save(items)
    return item


def delete(items, item_id):
    item = find(items, item_id)
    if item is None:
        return False
    items.remove(item)
    save(items)
    return True


if __name__ == "__main__":
    items = load()
    print("초기 데이터:", items)

    a = add(items, "apple", 100)
    b = add(items, "banana", 200)
    print("추가 후:", load())

    update(items, a["id"], value=150)
    print("수정 후:", load())

    delete(items, b["id"])
    print("삭제 후:", load())
