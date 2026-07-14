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


def find(items, item_id):
    return next((item for item in items if item["id"] == item_id), None)


def create(items):
    name = input("이름: ").strip()
    value = input("값: ").strip()
    item = {"id": next_id(items), "name": name, "value": value}
    items.append(item)
    save(items)
    print(f"생성됨: {item}")


def read_all(items):
    if not items:
        print("데이터가 없습니다.")
        return
    for item in items:
        print(item)


def read_one(items):
    key = input("검색할 ID 또는 이름: ").strip()
    matches = [item for item in items if str(item["id"]) == key or item["name"] == key]
    if not matches:
        print("일치하는 데이터가 없습니다.")
        return
    for item in matches:
        print(item)


def update(items):
    try:
        item_id = int(input("수정할 ID: ").strip())
    except ValueError:
        print("ERROR :: ID는 숫자여야 합니다.")
        return

    item = find(items, item_id)
    if item is None:
        print("해당 ID의 데이터가 없습니다.")
        return

    editable_fields = [key for key in item if key != "id"]
    field = input(f"수정할 필드 ({', '.join(editable_fields)}): ").strip()
    if field not in editable_fields:
        print("ERROR :: 수정할 수 없는 필드입니다.")
        return

    new_value = input("새 값: ").strip()
    item[field] = new_value
    save(items)
    print(f"수정됨: {item}")


def delete(items):
    try:
        item_id = int(input("삭제할 ID: ").strip())
    except ValueError:
        print("ERROR :: ID는 숫자여야 합니다.")
        return

    item = find(items, item_id)
    if item is None:
        print("해당 ID의 데이터가 없습니다.")
        return

    confirm = input(f"{item} 를 정말 삭제할까요? (y/N): ").strip().lower()
    if confirm != "y":
        print("삭제가 취소되었습니다.")
        return

    items.remove(item)
    save(items)
    print("삭제되었습니다.")


MENU = """===============================
1. Create
2. Read (전체 목록)
3. Read (ID/이름 검색)
4. Update
5. Delete
0. 종료
==============================="""


def main():
    items = load()

    while True:
        print(MENU)
        choice = input("선택 > ").strip()

        if choice == "0":
            print("종료합니다.")
            break
        elif choice == "1":
            create(items)
        elif choice == "2":
            read_all(items)
        elif choice == "3":
            read_one(items)
        elif choice == "4":
            update(items)
        elif choice == "5":
            delete(items)
        else:
            print("ERROR :: 올바른 메뉴 번호를 입력하세요.")


if __name__ == "__main__":
    main()
