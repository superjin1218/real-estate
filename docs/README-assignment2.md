# README.md

# Real Estate Field Wiki

## 제출 정보

| 항목 | 내용 |
| --- | --- |
| 이름 | 조진우 |
| 학번 | 12234195 |
| GitHub | https://github.com/superjin1218/real-estate |
| 공개 여부 | Public |

Real Estate Field Wiki는 전국 부동산 임장 기록, 후보 매물, 지역 특성, 온톨로지 단어를 Markdown Wiki로 관리하고, LLM Agent가 MCP Tool로 검색/추천/작성/그래프 탐색을 수행하는 Wiki Tool 프로젝트이다.

## 제출 산출물

| 파일 | 역할 |
| --- | --- |
| `DOMAIN.md` | 전국 임장 Wiki 도메인 정의 |
| `PRD.md` | 의사결정 라운드와 요구사항 |
| `README.md` | 실행 방법, MCP Tool, API 설명 |
| `AGENT_SPEC.md` | LLM Agent 역할과 권한 |
| `mvp.png` | 검색 중심 MVP GUI 화면 |

## 핵심 기능

- 첫 화면은 ChatGPT처럼 중앙 검색창 하나로 시작한다.
- 메뉴에서 `지도 탐색`, `아파트 찾기`, `임장 등록하기`, `Wiki 문서`, `후보 비교`로 이동한다.
- 대한민국 SVG 지도에서 시도를 클릭하면 해당 지역 요약 그래프가 나오고, node를 클릭하면 그 node 기준 1-hop 연결망으로 펼쳐진다.
- 자연어 질문은 온톨로지 단어로 정규화된다. 예: “소음이 없는 서울에 있는 집” → `서울특별시`, `low_noise`.
- 새 임장 글을 저장하면 본문 단어가 `ontology_terms`로 추출되고 관련 ontology Page와 자동 연결된다.
- 후보 비교는 첫 화면에서 제거하고 메뉴 내부 기능으로 숨겼다.

## Wiki Page 구성

`tools/generate_sample_wiki.py`는 전국 합성 Wiki Page 10,000개를 생성한다.

| Type | Count | Description |
| --- | ---: | --- |
| `region` | 267 | 시도/시군구 생활권 |
| `ontology` | 500 | 저소음, 역세권, 채광, 안전 등 개념 |
| `property` | 6,000 | 전국 후보 매물 |
| `field_note` | 3,000 | 임장 노트 |
| `checklist` | 200 | 지역별 확인 항목 |
| `trade_summary` | 33 | 실거래 샘플 요약 |

각 Page는 `province`, `district`, `ontology_terms`, `features`, `scores`, `related_pages` metadata를 가진다.

## 실행 방법

```bash
cd real-estate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tools/generate_sample_wiki.py
python3 -m uvicorn viewer.app:app --host 127.0.0.1 --port 8012
```

브라우저:

```text
http://127.0.0.1:8012/
```

MCP 서버:

```bash
python tools/mcp_server.py
```

## MCP Tool 목록

| Tool | Input | Output |
| --- | --- | --- |
| `list_pages` | `type?`, `tag?`, `province?`, `district?`, `limit?` | Page metadata 목록 |
| `get_page` | `page_id` | Page metadata + Markdown body |
| `search_pages` | `query`, `type?`, `tags?`, `province?`, `district?`, `limit?` | 검색 결과 |
| `get_related_pages` | `page_id` | 연결 Page 목록 |
| `get_atlas` | 없음 | 시도별 Page 수, 매물 수, 대표 ontology |
| `get_scoped_graph` | `province?`, `district?`, `limit?` | 지역 단위 node/edge 그래프 |
| `extract_ontology_terms` | `text` | 정규화된 ontology term 목록 |
| `recommend_properties` | `query`, `province?`, `district?`, `limit?` | 추천 매물, ontology path, 이유 |
| `create_field_note` | `raw_note`, `visited_at`, `region?`, `property?` | 임장 노트 초안 |
| `create_page` | `title`, `type`, `body`, `tags?`, `related_pages?`, `metadata?`, `confirmed?` | 새 Page 초안 또는 저장 결과 |
| `update_page` | `page_id`, `title?`, `body?`, `tags?`, `related_pages?`, `confirmed?` | 수정 초안 또는 저장 결과 |
| `compare_properties` | `property_page_ids` | 메뉴 내부 후보 비교표 |
| `fetch_apt_trade` | `lawd_cd`, `deal_ymd` | 매매 실거래 또는 샘플 |
| `fetch_apt_rent` | `lawd_cd`, `deal_ymd` | 전월세 실거래 또는 샘플 |

## API 예시

```bash
curl http://127.0.0.1:8012/api/atlas
curl "http://127.0.0.1:8012/api/graph?province=서울특별시&limit=500"
curl "http://127.0.0.1:8012/api/recommend?q=소음이%20없는%20서울에%20있는%20집%20찾아줘&limit=5"
```

추천 결과는 다음 구조를 포함한다.

```json
{
  "normalized": {
    "province": "서울특별시",
    "ontology_terms": ["low_noise"]
  },
  "recommendations": [
    {
      "page": {"id": "kr-property-00002", "title": "서울특별시 강남구 후보 0002 저소음 주거 블록"},
      "ontology_path": ["서울특별시", "강남구", "저소음", "후보 매물"],
      "reasons": ["저소음 조건과 연결됨", "서울특별시 지역 일치"]
    }
  ]
}
```

## 검증

```bash
python3 -m compileall tools viewer
python tools/mcp_server.py --self-test
find wiki/generated -type f -name '*.md' | wc -l
```

기대 결과:

- 생성 Page 수가 10,000개다.
- `recommend_properties("소음이 없는 서울에 있는 집 찾아줘")`가 `low_noise`와 서울 후보 매물을 반환한다.
- 첫 화면은 검색창 중심이고, 후보 비교는 메뉴에만 있다.
- 지도에서 서울을 선택하면 서울 부분 그래프가 펼쳐진다.

## 제한

- 생성 데이터는 실제 매물이 아니라 지역 특성을 반영한 합성 샘플이다.
- 투자 추천, 계약 판단, 법률/세금 자문은 범위에서 제외한다.
- 전체 10,000개 그래프는 한 번에 렌더링하지 않고 지역 단위 부분 그래프로 탐색한다.
