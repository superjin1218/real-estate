# Real Estate Field Wiki

부동산 임장 메모, 후보 매물, 체크리스트, 실거래 조회 결과를 Markdown Wiki로 정리하고, LLM Agent가 MCP Tool로 검색/조회/비교할 수 있게 만든 실행 가능한 Wiki 제품입니다.

API Key 없이도 샘플 데이터로 바로 실행됩니다. 실제 공공데이터 조회가 필요하면 `.env`에 `DATA_GO_KR_SERVICE_KEY`만 추가하면 됩니다.

## Repository Package

| Path | Purpose |
| --- | --- |
| `RULES.md` | Agent 운영 지침과 금지 규칙 |
| `skills/real-estate-wiki/SKILL.md` | Agent가 이 Wiki를 사용할 때 따르는 Skill |
| `raw/` | 사용자가 넣는 원본 메모 |
| `wiki/` | 화면과 MCP Tool이 읽는 Markdown Wiki Page |
| `schema/page.schema.json` | Wiki Page metadata 구조 |
| `tools/mcp_server.py` | MCP Tool 서버 |
| `tools/import_raw.py` | 원본 메모를 Wiki 초안으로 변환 |
| `viewer/` | FastAPI Wiki Viewer |
| `demo/mvp.png` | 실제 Wiki 화면 캡처 증명 |
| `docs/` | 도메인 정의, PRD, Agent SPEC 등 설계 문서 |

## 1. Install

Python 3.10 이상을 사용합니다.

```bash
git clone https://github.com/superjin1218/real-estate.git
cd real-estate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ubuntu 계열에서 `ensurepip is not available` 오류가 나면 먼저 venv 패키지를 설치합니다.

```bash
sudo apt install python3-venv
# 또는 Python 버전에 맞게: sudo apt install python3.12-venv
```

선택 사항:

```bash
cp .env.example .env
# .env 파일에 DATA_GO_KR_SERVICE_KEY 값을 넣으면 공공데이터 API를 호출합니다.
```

API Key를 넣지 않아도 `fetch_apt_trade`, `fetch_apt_rent`는 샘플 데이터를 반환하므로 화면과 Agent 검증이 가능합니다.

## 2. Run Viewer

```bash
uvicorn viewer.app:app --reload
```

브라우저에서 엽니다.

```text
http://127.0.0.1:8000
```

화면에서 확인할 수 있는 항목:

- 좌측: Wiki Page 목록
- 중앙: 선택한 Page 본문
- 우측: 관련 Page와 전월세 실거래 샘플
- 하단: 후보 매물 비교표
- 상단: 최근 호출된 Tool 이름

## 3. Add One Personal Note

처음 사용하는 사람은 `raw/my-first-note.md` 같은 파일을 하나 만듭니다.

```md
역에서 걸어서 10분 정도 걸렸다.
창은 동향이고 아침에는 밝았다.
큰길과 가까워 밤 소음은 다시 확인해야 한다.
관리비는 11만원이라고 들었지만 포함 항목은 확인하지 못했다.
```

원본 메모를 Wiki Page 초안으로 변환합니다.

```bash
python tools/import_raw.py raw/my-first-note.md \
  --visited-at 2026-06-16 \
  --region "잠실동" \
  --property "내 후보 매물 1"
```

생성된 파일은 `wiki/notes/` 아래에 저장됩니다. Viewer를 새로고침하면 좌측 Wiki 목록에서 확인할 수 있습니다.

## 4. MCP Tools

MCP 서버 실행:

```bash
python tools/mcp_server.py
```

Agent 설정 예시:

```json
{
  "mcpServers": {
    "real-estate-field-wiki": {
      "command": "python",
      "args": ["tools/mcp_server.py"],
      "cwd": "/absolute/path/to/real-estate"
    }
  }
}
```

Tool 목록:

| Tool | Input | Behavior |
| --- | --- | --- |
| `list_pages` | `type?`, `tag?` | Wiki Page metadata 목록 조회 |
| `get_page` | `page_id` | 특정 Page 본문과 metadata 조회 |
| `search_pages` | `query`, `type?`, `tags?` | 제목, 태그, 본문 검색 |
| `get_related_pages` | `page_id` | 연결된 Page 목록 조회 |
| `create_field_note` | `raw_note`, `visited_at`, `region?`, `property?` | 임장 메모를 Wiki 초안으로 변환 |
| `compare_properties` | `property_page_ids` | 후보 매물 비교표 생성 |
| `fetch_apt_trade` | `lawd_cd`, `deal_ymd` | 아파트 매매 실거래 조회 또는 샘플 반환 |
| `fetch_apt_rent` | `lawd_cd`, `deal_ymd` | 아파트 전월세 실거래 조회 또는 샘플 반환 |

## 5. Integration Request Pattern

Agent에게는 다음처럼 요청합니다.

```text
raw/my-first-note.md를 읽고 Wiki Page 초안을 만든 뒤,
기존 property/checklist Page와 연결할 수 있는 항목을 찾아줘.
근거가 되는 Wiki Page는 MCP Tool로 조회하고,
계약 추천은 하지 말고 확인 필요 항목만 정리해줘.
```

Agent는 `RULES.md`와 `skills/real-estate-wiki/SKILL.md`에 따라 파일을 추측해서 읽지 않고 MCP Tool 결과를 근거로 답해야 합니다.

## 6. Verify

로컬 Tool 자체 검증:

```bash
python tools/mcp_server.py --self-test
```

Viewer API 검증:

```bash
curl http://127.0.0.1:8000/api/pages
curl "http://127.0.0.1:8000/api/search?q=잠실%20소음"
curl "http://127.0.0.1:8000/api/compare?ids=property-jamsil-a,property-jamsil-b"
```

기대 결과:

- `page_count`가 1 이상이다.
- `search_pages` 결과에 잠실 관련 Page가 나온다.
- `compare_properties` 결과에 가격/비용, 교통, 소음/채광, 리스크 행이 나온다.
- API Key가 없으면 `source`가 `sample_data`로 표시된다.

## Safety

- API Key는 `.env`에만 둡니다.
- 부동산 계약, 투자, 법률, 세금 판단은 제공하지 않습니다.
- Wiki Page 또는 Tool 결과에 없는 정보는 사실처럼 쓰지 않습니다.
