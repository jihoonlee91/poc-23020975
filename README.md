# poc-23020975

JSON 파일 기반 데이터 저장/조회 PoC와, 그 구조를 활용한 CRUD 콘솔 애플리케이션.

- `poc.py` — PoC: JSON 파일을 읽고 쓰는 최소 기능 검증 (load/save/add/update/delete)
- `app.py` — PoC의 코드 구조(load/save/find)를 그대로 활용해 만든 CRUD 콘솔 앱

## 실행

```
python app.py
```

메뉴에서 Create/Read(전체 목록)/Read(ID·이름 검색)/Update/Delete를 선택해 사용합니다. 데이터는 `data.json`에 저장됩니다.

## 테스트

```
pip install pytest
pytest tests
```
