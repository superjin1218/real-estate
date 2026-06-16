# README.md

# Real Estate Field Wiki

Real Estate Field Wiki는 부동산 임장 기록, 매물 비교, 체크리스트, 아파트 실거래가 조회 결과를 Wiki Page로 관리하는 MCP 기반 Wiki Tool 프로젝트이다. 사용자는 GUI에서 Wiki Page를 탐색하고, AI Agent는 MCP 서버가 제공하는 Tool을 통해 Page 검색, 본문 조회, 관련 Page 연결, 임장 메모 초안 생성, 매물 비교, 공공데이터 API 조회를 수행한다.

## 0. 제출 산출물 구성

본 제출물은 Markdown 4종과 PNG 1종으로 구성된다.

| 파일 | 역할 |
| --- | --- |
| `DOMAIN.md` | Wiki 대상 지식 도메인 정의 |
| `PRD.md` | Agent와 의사결정 라운드를 거쳐 정한 프로젝트 요구사항 |
| `README.md` | 프로젝트 설명, MCP Tool 작동 방식, 실행 방법 |
| `AGENT_SPEC.md` | LLM Agent 역할, 권한, 허용 기능, 금지 기능 |
| `mvp.png` | Wiki Pages Serving MVP GUI 화면 |

## 1. 대상 도메인과 사용자

| 항목 | 내용 |
| --- | --- |
| 도메인 | 부동산 임장 기록 및 아파트 매물 비교 |
| 주요 사용자 | 자취방, 전월세, 매매 후보를 비교하는 초보 사용자 |
| 주요 지식 | 지역 정보, 매물 정보, 임장 노트, 체크리스트, 실거래가 요약 |
| 목표 | 흩어진 부동산 정보를 Wiki Page로 구조화하고 Agent가 안전하게 활용하게 함 |

## 2. 왜 이 Tool이 필요한가

부동산 매물 선택에는 가격뿐 아니라 교통, 소음, 채광, 관리비, 주변 환경, 실거래가, 계약 리스크 등 여러 지식이 필요하다. 사용자가 이 정보를 일반 메모로만 저장하면 비교가 어렵고, AI Agent가 어떤 근거를 사용했는지도 추적하기 어렵다.

MCP 서버는 AI Agent와 Wiki 데이터 사이의 표준 연결 계층이다. Agent는 직접 파일을 추측해서 읽지 않고, MCP Tool을 호출해 허용된 방식으로만 Wiki Page와 실거래 데이터를 조회한다. 이를 통해 사용자는 Agent의 기능과 권한을 문서화하고 통제할 수 있다.

## 3. 전체 구조

```text
User / GUI
  |
  | 검색, Page 선택, 매물 비교 요청
  v
Wiki GUI
  |
  | HTTP 또는 MCP Client 요청
  v
MCP Server
  |
  |-- Wiki Page Store
  |     |-- Markdown pages
  |     |-- metadata index
  |
  |-- Public Data Adapter
  |     |-- 국토교통부 아파트 매매 실거래가 API
  |     |-- 국토교통부 아파트 전월세 실거래가 API
  |     |-- sample fallback data
  |
  v
LLM Agents
  |-- Wiki Search Agent
  |-- Field Note Editor Agent
  |-- Property Comparison Agent
  |-- Data Retrieval Agent
```

## 4. Wiki Pages 구현과 Serving

Wiki Page는 Markdown 파일과 메타데이터로 구성된다. MCP 서버는 Page 목록과 본문을 읽어 Tool 응답으로 반환하고, GUI는 이를 Page 목록, 본문, 관련 Page, Tool 결과 패널로 시각화한다.

예상 Page 구조는 다음과 같다.

```text
pages/
  regions/songpa-gu.md
  properties/property-jamsil-a.md
  properties/property-office-b.md
  notes/field-note-2026-06-14.md
  checklists/lease-risk-checklist.md
  data/trade-summary-jamsil.md
```

GUI 시각화 방식은 다음과 같다.

| 영역 | 역할 |
| --- | --- |
| 상단 검색창 | Wiki Page와 실거래 데이터를 검색 |
| 좌측 패널 | Page 목록, 타입, 태그 필터 표시 |
| 중앙 패널 | 선택된 Wiki Page 본문 표시 |
| 우측 패널 | 관련 Page, Agent 요약, API 조회 결과 표시 |
| 하단 패널 | 선택한 매물 간 비교표 표시 |

## 5. MCP Tool 목록

### 5.1 `list_pages`

| 항목 | 내용 |
| --- | --- |
| 목적 | 사용 가능한 Wiki Page 목록 조회 |
| 입력 | `type?`, `tag?` |
| 출력 | Page ID, 제목, 타입, 태그, 수정일 |
| Agent 사용 방식 | Agent가 어떤 Page를 조회할 수 있는지 먼저 파악 |

### 5.2 `get_page`

| 항목 | 내용 |
| --- | --- |
| 목적 | 특정 Wiki Page 본문 조회 |
| 입력 | `page_id` 또는 `slug` |
| 출력 | 메타데이터와 Markdown 본문 |
| Agent 사용 방식 | 답변 근거가 되는 원문 Page를 읽음 |

### 5.3 `search_pages`

| 항목 | 내용 |
| --- | --- |
| 목적 | 키워드, 태그, Page 타입 기반 검색 |
| 입력 | `query`, `type?`, `tags?` |
| 출력 | 검색 결과 Page 목록과 간단 요약 |
| Agent 사용 방식 | 사용자의 질문과 관련된 Page를 찾음 |

### 5.4 `get_related_pages`

| 항목 | 내용 |
| --- | --- |
| 목적 | 특정 Page와 연결된 관련 Page 조회 |
| 입력 | `page_id` |
| 출력 | 관련 Page ID, 관계 유형, 제목 |
| Agent 사용 방식 | 매물 Page에서 지역 Page, 체크리스트, 임장 노트로 이동 |

### 5.5 `create_field_note`

| 항목 | 내용 |
| --- | --- |
| 목적 | 비정형 임장 메모를 Wiki Page 초안으로 변환 |
| 입력 | `raw_note`, `visited_at`, `region?`, `property?` |
| 출력 | Markdown 초안, 태그, 확인 필요 항목 |
| Agent 사용 방식 | Field Note Editor Agent가 초안을 생성하되 사용자의 승인 전 확정 저장하지 않음 |

### 5.6 `compare_properties`

| 항목 | 내용 |
| --- | --- |
| 목적 | 여러 매물 Page를 기준 항목별로 비교 |
| 입력 | `property_page_ids` |
| 출력 | 가격, 면적, 교통, 소음, 관리비, 리스크 비교표 |
| Agent 사용 방식 | Property Comparison Agent가 투자 추천이 아닌 근거 기반 비교를 수행 |

### 5.7 `fetch_apt_trade`

| 항목 | 내용 |
| --- | --- |
| 목적 | 아파트 매매 실거래가 조회 |
| 입력 | `lawd_cd`, `deal_ymd` |
| 출력 | 단지명, 법정동, 면적, 거래금액, 계약일, 층, 건축년도 |
| 외부 API | 국토교통부_아파트 매매 실거래가 자료 |

공식 API: https://www.data.go.kr/data/15126469/openapi.do

### 5.8 `fetch_apt_rent`

| 항목 | 내용 |
| --- | --- |
| 목적 | 아파트 전월세 실거래가 조회 |
| 입력 | `lawd_cd`, `deal_ymd` |
| 출력 | 단지명, 법정동, 면적, 보증금, 월세, 계약일, 층, 계약기간 |
| 외부 API | 국토교통부_아파트 전월세 실거래가 자료 |

공식 API: https://www.data.go.kr/data/15126474/openapi.do

## 6. MCP Tool 인터페이스 예시

아래 예시는 Agent가 MCP 서버를 통해 Tool을 호출할 때 기대하는 최소 입출력 형태이다.

### 6.1 `search_pages`

```json
{
  "name": "search_pages",
  "input": {
    "query": "잠실 전세 소음",
    "type": "property",
    "tags": ["rent", "noise"]
  },
  "output": {
    "results": [
      {
        "page_id": "property-jamsil-a",
        "title": "잠실 후보 A 임장 노트",
        "type": "property",
        "matched_fields": ["title", "tags", "body"]
      }
    ]
  }
}
```

### 6.2 `get_page`

```json
{
  "name": "get_page",
  "input": {
    "page_id": "property-jamsil-a"
  },
  "output": {
    "page_id": "property-jamsil-a",
    "title": "잠실 후보 A 임장 노트",
    "type": "property",
    "tags": ["jamsil", "rent", "noise"],
    "body": "## 관찰 내용\\n- 지하철역까지 도보 약 8분..."
  }
}
```

### 6.3 `compare_properties`

```json
{
  "name": "compare_properties",
  "input": {
    "property_page_ids": ["property-jamsil-a", "property-jamsil-b"]
  },
  "output": {
    "comparison": [
      {
        "criterion": "역 접근성",
        "property-jamsil-a": "도보 8분",
        "property-jamsil-b": "도보 13분"
      }
    ],
    "risk_notes": ["관리비 항목 재확인 필요"],
    "disclaimer": "정보 비교이며 투자 또는 계약 추천이 아닙니다."
  }
}
```

### 6.4 `fetch_apt_rent`

```json
{
  "name": "fetch_apt_rent",
  "input": {
    "lawd_cd": "11710",
    "deal_ymd": "202405"
  },
  "output": {
    "source": "sample_data",
    "fallback_reason": "DATA_GO_KR_SERVICE_KEY is not configured",
    "items": [
      {
        "apt_name": "샘플아파트",
        "exclusive_area": "84.9",
        "deposit": "50000",
        "monthly_rent": "0",
        "deal_day": "15"
      }
    ]
  }
}
```

## 7. 외부 API 작동 방식

공공데이터포털 API는 활용신청 후 발급받은 `serviceKey`가 필요하다. 실거래가 조회 Tool은 다음 기준으로 동작한다.

```text
1. .env에서 DATA_GO_KR_SERVICE_KEY를 읽는다.
2. serviceKey가 있으면 공공데이터 API를 호출한다.
3. serviceKey가 없거나 API 호출이 실패하면 sample data를 반환한다.
4. 응답에는 source 필드를 포함해 public_api 또는 sample_data를 구분한다.
```

공통 요청 파라미터:

| 파라미터 | 설명 | 예시 |
| --- | --- | --- |
| `serviceKey` | 공공데이터포털 인증키 | `.env`에 저장 |
| `LAWD_CD` | 법정동 코드 앞 5자리 | `11710` |
| `DEAL_YMD` | 계약년월 6자리 | `202405` |

실제 호출 URL 형태는 다음과 같다.

```text
https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade
https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent
```

## 8. 실행 방법

아래 실행 방법은 실제 구현 시 기준이다.

### 8.1 환경

```text
Python 3.11+
공공데이터포털 serviceKey, 선택 사항
```

### 8.2 의존성 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install mcp fastapi uvicorn requests python-dotenv
```

### 8.3 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 예시:

```text
DATA_GO_KR_SERVICE_KEY=your_service_key_here
WIKI_PAGE_DIR=./pages
SAMPLE_DATA_DIR=./sample_data
```

API 키가 없으면 `DATA_GO_KR_SERVICE_KEY`를 비워 두고 샘플 데이터로 실행한다.

### 8.4 MCP 서버 실행

```bash
python server.py
```

### 8.5 GUI 실행

```bash
uvicorn app:app --reload --port 8000
```

브라우저에서 다음 주소로 접속한다.

```text
http://localhost:8000
```

## 9. MVP 사용 흐름

1. 사용자가 GUI 검색창에 `잠실 전세 소음`을 입력한다.
2. GUI가 `search_pages` Tool을 호출한다.
3. Agent가 관련 매물 Page와 체크리스트 Page를 찾는다.
4. 사용자가 매물 Page를 선택하면 `get_page`와 `get_related_pages` Tool이 호출된다.
5. 우측 패널에 관련 임장 노트와 실거래가 조회 결과가 표시된다.
6. 사용자가 매물 2개를 선택하면 `compare_properties` Tool이 비교표를 생성한다.

## 10. Agent 흐름

```text
사용자 질문
  -> Wiki Search Agent가 search_pages 호출
  -> 필요한 Page를 get_page로 조회
  -> 관련 Page를 get_related_pages로 확장
  -> 실거래가가 필요하면 Data Retrieval Agent가 fetch_apt_trade/fetch_apt_rent 호출
  -> Property Comparison Agent가 비교표 생성
  -> 최종 응답에는 사용한 Tool과 근거 Page를 표시
```

## 11. 현재 한계와 다음 단계

### 현재 한계

- MVP는 투자 추천을 제공하지 않는다.
- 법률, 세금, 대출 판단은 범위에서 제외한다.
- 외부 API 키가 없으면 실거래 데이터는 샘플 데이터로 대체된다.
- 지도 기반 시각화는 포함하지 않는다.

### 다음 단계

- 실제 Markdown Page Store 구현
- MCP 서버의 Tool 함수 구현
- 공공데이터 API 응답 XML/JSON 파싱
- GUI에서 Page 링크 그래프 시각화 추가
- 사용자 승인 기반 Wiki Page 저장 기능 추가
