# Real Estate Field Wiki 도메인 정의서

## 1. 도메인 개요

Real Estate Field Wiki는 전국 부동산 임장 기록, 후보 매물, 지역 특성, 실거래 요약, 체크리스트, 온톨로지 단어를 Markdown Wiki로 관리하는 MCP 기반 LLM Wiki이다.

사용자는 "소음이 없는 서울에 있는 집 찾아줘"처럼 자연어로 질문하고, Agent는 Wiki에 저장된 지역/매물/온톨로지 Page를 연결해 후보를 찾는다. 새 임장 글이 추가되면 본문에 포함된 단어가 온톨로지 term으로 추출되고 관련 ontology Page와 자동 연결된다.

## 2. 무엇을 만들 것인가

본 프로젝트는 잠실 예시 하나에 머무르지 않고 전국 단위의 밀도 있는 임장 지식 연결망을 만든다.

| 구분 | 설명 | 예시 |
| --- | --- | --- |
| 지역 Page | 시도/시군구 생활권, 교통, 상권, 학교, 녹지, 소음 특성 | `kr-region-seoul-gangnam-gu` |
| 매물 Page | 후보 아파트/주거 블록의 특징, 점수, 장단점 | `kr-property-00002` |
| 임장 노트 | 방문 관찰, 소음/채광/동선/상권 메모 | `kr-note-00024` |
| 체크리스트 | 지역별 확인 항목과 임장 질문 | `kr-checklist-seoul-001` |
| 실거래 요약 | 샘플 실거래 흐름과 조회 기준 | `kr-trade-seoul-001` |
| 온톨로지 Page | 저소음, 역세권, 채광, 공원, 학군 등 검색 개념 | `kr-ontology-seoul-low-noise` |

## 3. 왜 LLM Wiki 방식인가

부동산 탐색은 지역, 매물, 임장 기록, 가격 흐름, 생활 조건이 동시에 연결되는 문제다. 단순 목록 UI는 사용자가 맥락을 직접 이어 붙여야 하고, 전체 그래프를 한 화면에 뿌리면 지식연결망이 정신없어진다.

이 프로젝트는 다음 방식으로 문제를 푼다.

- 첫 화면은 ChatGPT처럼 검색창 하나로 시작한다.
- 전국 지도에서 시도를 고르면 해당 지역의 부분 그래프만 펼친다.
- Obsidian처럼 Page node와 related edge를 보여주되, 전체 10,000개 그래프를 한 번에 렌더링하지 않는다.
- 자연어 질문을 `low_noise`, `transit_access`, `green_space` 같은 온톨로지 term으로 정규화한다.
- 새 Page 작성 시 본문/태그를 온톨로지화해 연결망을 자동 보강한다.

## 4. 대상 사용자

| 사용자 | 사용 목적 |
| --- | --- |
| 자취/전월세 탐색자 | 소음, 역 접근성, 관리비, 안전 조건을 기준으로 후보 탐색 |
| 신혼부부/실거주자 | 서울/수도권/지방 주요 지역의 생활권 비교 |
| 임장 기록 사용자 | 방문 메모를 Wiki Page로 축적하고 다시 검색 |
| AI Agent | MCP Tool로 Wiki를 검색, 추천, 작성, 그래프 탐색 |

## 5. 데이터 범위

### 포함 범위

- 전국 17개 시도, 250개 시군구 수준의 합성 지역 지식
- 총 10,000개 생성 Wiki Page
- 지역별 특징을 반영한 후보 매물 6,000개
- 임장 노트 3,000개
- 온톨로지 Page 500개
- 체크리스트 200개
- 실거래 샘플 요약 33개
- 사용자 작성 Page와 자동 온톨로지 연결
- 국토교통부 아파트 매매/전월세 실거래 API 또는 샘플 fallback

### 제외 범위

- 실제 매물 크롤링
- 투자 수익률 예측
- 계약 체결 추천
- 법률, 세금, 대출 자문
- 개인정보가 포함된 상세 주소, 전화번호, 소유자 정보 저장
- 전체 10,000개 node를 한 화면에서 강제로 렌더링하는 방식

## 6. Wiki Page 구조

MVP의 Wiki Page는 Markdown 파일과 metadata header로 저장된다.

```text
wiki/
  pages/
    regions/
    properties/
    notes/
    checklists/
    data/
  generated/
    regions/
    ontology/
    properties/
    notes/
    checklists/
    data/
```

주요 metadata는 다음과 같다.

| 필드 | 설명 |
| --- | --- |
| `id` | Page 고유 식별자 |
| `title` | Page 제목 |
| `type` | `region`, `ontology`, `property`, `field_note`, `checklist`, `trade_summary` |
| `province` | 시도 |
| `district` | 시군구 |
| `ontology_terms` | 정규화된 온톨로지 term |
| `features` | 매물/지역 특징 |
| `scores` | 소음, 교통, 채광 등 샘플 점수 |
| `tags` | 검색과 연결에 사용할 태그 |
| `related_pages` | 연결된 Wiki Page ID |
| `source` | 사용자 작성, 생성 샘플, API fallback 등 출처 |
| `updated_at` | 마지막 수정일 |

## 7. 시각화 방식

MVP 화면은 첫 진입과 탐색 화면을 분리한다.

| 화면 | 역할 |
| --- | --- |
| 첫 화면 | 중앙 검색창 하나로 자연어 질문 입력 |
| 메뉴 | 지도 탐색, 아파트 찾기, 임장 등록하기, Wiki 문서, 후보 비교 진입 |
| 지도 탐색 | 대한민국 SVG 지도에서 시도 선택 |
| 부분 그래프 | 선택한 시도/시군구의 Wiki node와 edge를 Obsidian식으로 표시 |
| 아파트 찾기 | 자연어를 온톨로지 term으로 변환하고 후보 매물 추천 |
| 임장 등록하기 | 새 Page 저장 및 온톨로지 자동 연결 |
| 후보 비교 | 첫 화면에서 숨기고 메뉴 내부에서만 제공 |

## 8. 필요한 MCP Tool

| Tool | 필요한 이유 |
| --- | --- |
| `list_pages` | 지역/타입/태그별 Wiki Page 목록 조회 |
| `get_page` | 특정 Page 본문과 metadata 조회 |
| `search_pages` | 자연어, 태그, 지역 기반 검색 |
| `get_related_pages` | Page 간 연결 관계 조회 |
| `get_atlas` | 전국 시도별 Page/매물/온톨로지 요약 |
| `get_scoped_graph` | 선택 지역의 부분 지식그래프 조회 |
| `extract_ontology_terms` | 본문과 질문에서 온톨로지 term 추출 |
| `recommend_properties` | 온톨로지 조건 기반 후보 매물 추천 |
| `create_field_note` | 임장 메모를 Wiki 초안으로 구조화 |
| `create_page` | 사용자 승인 후 새 Page 저장 및 ontology 자동 연결 |
| `update_page` | 기존 Page 수정 및 ontology 자동 보강 |
| `compare_properties` | 메뉴 내부 후보 비교표 생성 |
| `fetch_apt_trade` | 아파트 매매 실거래 조회 또는 샘플 반환 |
| `fetch_apt_rent` | 아파트 전월세 실거래 조회 또는 샘플 반환 |

## 9. MVP 성공 기준

- 첫 화면이 검색 중심 UI로 표시된다.
- 메뉴에서 지도 탐색, 아파트 찾기, 임장 등록하기, Wiki 문서, 후보 비교로 이동할 수 있다.
- `tools/generate_sample_wiki.py`로 정확히 10,000개 generated Page가 생성된다.
- `get_atlas`가 전국 17개 시도 요약을 반환한다.
- 서울을 선택하면 서울 부분 그래프가 표시된다.
- "소음이 없는 서울에 있는 집 찾아줘"가 `서울특별시`, `low_noise`로 정규화되고 후보 매물을 반환한다.
- 새 Page 저장 시 `ontology_terms`와 관련 ontology Page가 자동 연결된다.
- 후보 비교는 첫 화면에 노출되지 않고 메뉴 안에 있다.

## 10. 설계 핵심 질문 요약

| 질문 | 답변 |
| --- | --- |
| 무엇을 만들 것인가? | 전국 임장 지식을 Page와 ontology로 연결하는 LLM Wiki Tool |
| 왜 만들 것인가? | 부동산 탐색 조건을 검색어가 아니라 연결 가능한 지식 구조로 다루기 위해 |
| 어떻게 만들 것인가? | Markdown Wiki Store, MCP Tool, FastAPI Viewer, 전국 생성 데이터, 온톨로지 추천 엔진으로 구현 |
| 어떻게 시각화할 것인가? | 첫 화면은 검색창 하나, 이후 지도 기반 지역 선택과 Obsidian식 부분 그래프 |
| Agent는 어떻게 연결되는가? | Agent는 파일에 직접 접근하지 않고 MCP Tool로 Page 검색, 추천, 작성, 그래프 조회를 수행 |

## 11. 도메인 선택 근거

부동산 임장은 지역성, 반복 관찰, 사용자 메모, 공공데이터, 후보 비교, 검색 의도가 모두 얽힌 실제 생활 도메인이다. 따라서 MCP Tool이 왜 필요한지, Wiki Page Serving이 어떤 가치를 갖는지, LLM이 어떻게 지식 연결망을 활용할 수 있는지를 한 프로젝트 안에서 보여주기 적합하다.
