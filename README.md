# Real Estate Field Wiki

## Submission

| Field | Value |
| --- | --- |
| 이름 | 조진우 |
| 학번 | 12234195 |
| GitHub | https://github.com/superjin1218/real-estate |
| 공개 여부 | Public |

전국 부동산 임장 기록을 LLM Wiki로 관리하는 MCP 기반 Wiki Tool입니다. 첫 화면은 검색창 하나로 시작하고, 메뉴에서 지도 탐색, 아파트 찾기, 임장 등록하기, Wiki 문서, 후보 비교로 이동합니다.

현재 `tools/generate_sample_wiki.py`는 전국 합성 Wiki Page 10,000개를 생성합니다. 지역 267개, 온톨로지 500개, 매물 6,000개, 임장 노트 3,000개, 체크리스트 200개, 실거래 샘플 33개로 구성되며 각 Page는 `related_pages`와 `ontology_terms`로 연결됩니다.

## Core Experience

- 첫 화면: ChatGPT처럼 중앙 검색창만 보이는 검색 중심 UI
- 지도 탐색: 대한민국 SVG 지도에서 시도를 누르면 해당 지역 요약 그래프를 표시하고, node를 누르면 그 node 기준 1-hop 연결망으로 펼침
- 아파트 찾기: “소음이 없는 서울에 있는 집 찾아줘” 같은 자연어를 `low_noise`, `서울특별시` 등 온톨로지 조건으로 정규화해 후보 매물 추천
- 임장 등록하기: 새 글을 저장할 때 본문/태그 단어를 온톨로지화하고 관련 ontology Page와 자동 연결
- 후보 비교: 첫 화면에서는 제거하고 메뉴 안에 숨김

## Repository Package

| Path | Purpose |
| --- | --- |
| `wiki/` | Markdown Wiki Page store |
| `tools/wiki_store.py` | Wiki 검색, 그래프, 온톨로지 추천, 저장 로직 |
| `tools/mcp_server.py` | MCP Tool 서버 |
| `tools/generate_sample_wiki.py` | 전국 10,000개 합성 Wiki Page 생성기 |
| `viewer/` | FastAPI Viewer와 검색/지도/그래프 UI |
| `schema/page.schema.json` | Wiki Page metadata schema |
| `docs/` | 과제 제출용 DOMAIN/PRD/README/AGENT_SPEC |
| `demo/mvp.png` | MVP 화면 캡처 |

## Install

```bash
cd real-estate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate National Wiki

```bash
python tools/generate_sample_wiki.py
```

기대 결과:

```text
generated_pages: 10000
regions: 267
ontology: 500
properties: 6000
notes: 3000
checklists: 200
trade_summaries: 33
```

## Run Viewer

```bash
python3 -m uvicorn viewer.app:app --host 127.0.0.1 --port 8012
```

브라우저:

```text
http://127.0.0.1:8012/
```

## MCP Server

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

## MCP Tools

| Tool | Purpose |
| --- | --- |
| `list_pages` | Wiki Page 목록 조회, `type`, `tag`, `province`, `district`, `limit` 지원 |
| `get_page` | Page metadata와 Markdown 본문 조회 |
| `search_pages` | 키워드/태그/지역 기반 검색 |
| `get_related_pages` | 특정 Page의 연결 Page 조회 |
| `get_knowledge_graph` | 전체 그래프 반환, 대량 응답 주의 |
| `get_atlas` | 시도별 Page 수, 매물 수, 대표 온톨로지 반환 |
| `get_scoped_graph` | 시도/시군구 단위 부분 그래프 반환 |
| `extract_ontology_terms` | 자연어/본문에서 온톨로지 term 추출 |
| `recommend_properties` | 자연어 조건을 온톨로지화해 후보 매물 추천 |
| `create_field_note` | 비정형 임장 메모를 초안으로 변환 |
| `create_page` | 승인 기반 새 Wiki Page 저장, ontology 자동 연결 |
| `update_page` | 승인 기반 기존 Page 수정, ontology 자동 보강 |
| `compare_properties` | 메뉴 안 후보 비교용 비교표 생성 |
| `fetch_apt_trade` | 아파트 매매 실거래 조회 또는 샘플 반환 |
| `fetch_apt_rent` | 아파트 전월세 실거래 조회 또는 샘플 반환 |

## HTTP API

```bash
curl http://127.0.0.1:8012/api/atlas
curl "http://127.0.0.1:8012/api/graph?province=서울특별시&limit=500"
curl "http://127.0.0.1:8012/api/recommend?q=소음이%20없는%20서울에%20있는%20집%20찾아줘&limit=5"
curl "http://127.0.0.1:8012/api/pages?province=서울특별시&type=property&limit=20"
```

추천 응답은 `normalized.ontology_terms`, `ontology_path`, 추천 매물, 근거 문장을 포함합니다.

## Verify

```bash
python3 -m compileall tools viewer
python tools/mcp_server.py --self-test
find wiki/generated -type f -name '*.md' | wc -l
```

기대 결과:

- generated Page 수가 `10000`
- self-test의 `recommend_sample`이 `서울특별시`, `low_noise`, 추천 매물을 반환
- `/api/atlas`가 17개 시도 요약 반환
- `/api/graph?province=서울특별시`가 서울 부분 그래프 반환

## Safety

- 생성 샘플은 실제 매물 데이터가 아니라 MVP 검증용 합성 데이터입니다.
- Agent는 투자, 계약, 법률, 세금 판단을 하지 않습니다.
- 새 Page 쓰기는 승인 기반이며 삭제 Tool은 제공하지 않습니다.
