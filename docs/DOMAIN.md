# DOMAIN.md

# Real Estate Field Wiki 도메인 정의서

## 1. 도메인 개요

본 프로젝트의 Wiki 도메인은 **부동산 임장 기록 및 아파트 매물 비교 지식 관리**이다. 사용자는 여러 지역과 매물을 방문하면서 얻은 관찰 내용, 체크리스트, 실거래가 조회 결과, 장단점 비교 결과를 Wiki Page로 저장하고 검색한다.

프로젝트명은 **Real Estate Field Wiki**이며, 주요 목적은 초보 임차인 또는 매수 희망자가 흩어진 부동산 정보를 구조화된 Wiki 형태로 정리하고, AI Agent가 MCP Tool을 통해 필요한 페이지와 데이터를 검색, 요약, 비교할 수 있게 하는 것이다.

## 2. 무엇을 만들 것인가

Real Estate Field Wiki는 다음 지식을 다룬다.

| 구분 | 설명 | 예시 Wiki Page |
| --- | --- | --- |
| 지역 정보 | 임장 대상 지역의 교통, 생활 편의, 소음, 치안, 학교, 상권 정보 | `songpa-gu.md`, `suwon-yeongtong.md` |
| 매물 정보 | 후보 매물의 가격, 면적, 층, 관리비, 장점, 단점, 위험 요소 | `property-jamsil-a.md`, `property-office-b.md` |
| 임장 기록 | 방문 날짜, 관찰 내용, 사진 메모, 주변 환경, 재방문 필요 여부 | `field-note-2026-06-14.md` |
| 체크리스트 | 채광, 누수, 소음, 주차, 관리비, 전세 리스크, 등기 확인 항목 | `lease-risk-checklist.md` |
| 실거래 요약 | 공공데이터 API 또는 샘플 데이터에서 조회한 매매/전월세 실거래 정보 | `trade-summary-jamsil.md` |

## 3. 왜 Wiki 방식이 필요한가

부동산 의사결정은 단일 검색 결과만으로 끝나지 않는다. 사용자는 지역, 매물, 임장 기록, 실거래가, 체크리스트를 반복적으로 비교해야 한다. 일반 메모 앱은 검색과 연결 관계를 수동으로 관리해야 하며, AI Agent가 필요한 근거를 안정적으로 찾기 어렵다.

Wiki 방식은 다음 장점이 있다.

- 각 매물과 지역을 독립된 Page로 관리할 수 있다.
- 관련 Page를 링크해 지역, 매물, 임장 노트, 체크리스트를 연결할 수 있다.
- MCP Tool이 Page 목록, 본문, 관련 Page, 실거래 조회 결과를 구조화된 JSON으로 Agent에게 제공할 수 있다.
- Agent가 사용자의 질문에 대해 기존 Wiki 근거를 먼저 조회하므로 임의 추측을 줄일 수 있다.

## 4. 대상 사용자

| 사용자 | 사용 목적 |
| --- | --- |
| 대학생/사회초년생 | 자취방 후보를 비교하고 전월세 체크리스트를 확인 |
| 신혼부부/실거주자 | 지역별 아파트 후보와 실거래가를 비교 |
| 부동산 공부 사용자 | 임장 기록을 축적하고 지역별 관찰 지식을 구조화 |
| AI Agent | Wiki Page를 검색, 조회, 요약, 비교하고 사용자의 질문에 답변 |

## 5. 데이터 범위

### 포함 범위

- 사용자가 직접 작성한 임장 메모
- 매물별 장단점과 확인 필요 사항
- 지역별 생활 인프라 관찰 정보
- 공공데이터포털 국토교통부 아파트 매매/전월세 실거래가 API 조회 결과
- API 키가 없을 때 사용할 샘플 실거래 데이터
- Wiki Page 간 관련 링크와 태그

### 제외 범위

- 투자 수익률 예측
- 매수/매도 추천
- 법률 자문
- 세금 계산
- 대출 가능 여부 판단
- 실시간 지도, 교통 API, 상권 매출 API 연동
- 개인정보가 포함된 상세 주소, 전화번호, 소유자 정보 저장

## 6. Wiki Page 구조

MVP의 Wiki Page는 Markdown 기반 문서로 관리한다.

```text
pages/
  regions/
    songpa-gu.md
    suwon-yeongtong.md
  properties/
    property-jamsil-a.md
    property-office-b.md
  notes/
    field-note-2026-06-14.md
  checklists/
    lease-risk-checklist.md
    sunlight-noise-checklist.md
  data/
    trade-summary-jamsil.md
```

각 Page는 다음 메타데이터를 가진다.

| 필드 | 설명 |
| --- | --- |
| `id` | Page 고유 식별자 |
| `title` | Page 제목 |
| `type` | `region`, `property`, `field_note`, `checklist`, `trade_summary` |
| `tags` | 검색과 관련 Page 추천에 사용할 태그 |
| `source` | 사용자 작성, 샘플 데이터, 공공데이터 API 등 출처 |
| `updated_at` | 마지막 수정일 |
| `related_pages` | 연결된 Wiki Page 목록 |

## 7. Wiki Pages 시각화 방식

MVP GUI는 Wiki 정보를 한 화면에서 탐색할 수 있도록 구성한다.

```text
상단: 검색창, 현재 선택된 Tool 상태
좌측: Wiki Page 목록과 태그 필터
중앙: 선택한 Wiki Page 본문
우측: 관련 Page, API 조회 결과, Agent 요약
하단: 선택한 매물 간 비교 테이블
```

이 구조는 사용자가 Page를 읽는 동시에 관련 체크리스트와 실거래 데이터를 확인할 수 있게 한다. 또한 Agent가 어떤 MCP Tool을 통해 어떤 정보를 가져왔는지 확인할 수 있어 Tool-Agent 연결 흐름을 명확히 보여준다.

## 8. 필요한 MCP Tool

| Tool | 필요한 이유 |
| --- | --- |
| `list_pages` | Agent가 사용 가능한 Wiki Page 목록과 메타데이터를 파악 |
| `get_page` | 특정 Page 본문을 정확히 조회 |
| `search_pages` | 키워드, 태그, Page 타입 기준으로 관련 지식 검색 |
| `get_related_pages` | 매물, 지역, 체크리스트 사이의 연결 관계 조회 |
| `create_field_note` | 사용자의 임장 메모를 Wiki Page 초안으로 구조화 |
| `compare_properties` | 여러 매물 Page를 기준 항목별로 비교 |
| `fetch_apt_trade` | 국토교통부 아파트 매매 실거래가 자료 조회 |
| `fetch_apt_rent` | 국토교통부 아파트 전월세 실거래가 자료 조회 |

## 9. MVP 성공 기준

- Wiki Page 목록과 상세 Page가 GUI에서 확인된다.
- 검색어로 관련 Page를 찾을 수 있다.
- 선택한 Page의 관련 Page가 표시된다.
- 샘플 매물 2개 이상을 비교할 수 있다.
- 실거래가 조회 Tool은 API 키가 있으면 공공데이터를 호출하고, 없으면 샘플 데이터를 반환하도록 설계된다.
- Agent SPEC에 정의된 권한에 따라 읽기, 초안 생성, 비교 기능이 분리된다.

## 10. 설계 핵심 질문 요약

| 질문 | 답변 |
| --- | --- |
| 무엇을 만들 것인가? | 부동산 임장 기록, 매물 비교, 체크리스트, 실거래가 조회 결과를 Wiki Page로 서빙하는 MCP 기반 Wiki Tool을 만든다. |
| 왜 만들 것인가? | 부동산 후보 비교에는 여러 출처의 정보가 필요하며, 이를 Wiki로 구조화해야 사용자가 다시 찾고 Agent가 근거 기반으로 답변할 수 있다. |
| 어떻게 만들 것인가? | Markdown Wiki Page Store를 만들고, MCP 서버가 `list_pages`, `get_page`, `search_pages`, `get_related_pages`, `compare_properties`, `fetch_apt_trade`, `fetch_apt_rent` Tool로 데이터를 제공한다. |
| Wiki Pages를 어떻게 시각화할 것인가? | 좌측 Page 목록, 중앙 Page 본문, 우측 관련 Page/API 결과, 하단 매물 비교표를 가진 GUI로 시각화한다. |
| 이 도구를 활용하려면 어떤 기능이 필요한가? | Page 목록 조회, 본문 조회, 검색, 관련 Page 탐색, 임장 메모 초안화, 매물 비교, 실거래가 조회 기능이 필요하다. |
| Tool과 Agent는 어떻게 연결되는가? | Agent는 파일에 직접 접근하지 않고 MCP 서버의 허용 Tool만 호출한다. Tool 응답은 JSON 형태로 Agent에게 전달되어 요약, 비교, 질의응답에 사용된다. |

## 11. 도메인 선택 근거

본 도메인은 강의 주제 자체를 Wiki로 재현하지 않고, 실제 생활 문제를 대상으로 MCP Tool의 필요성을 설명한다. 또한 외부 API, 로컬 Wiki Page, Agent 권한 분리를 모두 보여줄 수 있어 "Wiki Pages 구현과 Serving", "Tools and Agent", "MCP 서버 필요성"을 한 프로젝트 안에서 자연스럽게 설명할 수 있다.
