# Real Estate Field Wiki PRD

## 1. 배경

부동산 후보를 찾을 때 사용자는 지역 특성, 소음, 교통, 채광, 관리비, 임장 메모, 실거래 흐름을 따로 확인한다. 이 정보가 흩어지면 "조용한 서울 집"처럼 실제 의도에 가까운 질문을 해도 자료를 다시 조합해야 한다.

Real Estate Field Wiki는 전국 임장 지식을 Wiki Page와 온톨로지 term으로 연결하고, LLM Agent가 MCP Tool을 통해 검색, 추천, 작성, 부분 그래프 탐색을 수행하도록 만든다.

## 2. 문제 정의

- 잠실 같은 단일 예시만 있으면 지식그래프가 성기고 데모가 제한된다.
- 전체 그래프를 한 화면에 표시하면 node/edge가 과밀해져 탐색이 어렵다.
- 후보 비교가 첫 화면에 나오면 사용자가 원하는 "질문부터 시작하는" 경험이 흐려진다.
- 임장 글을 새로 추가해도 단어가 연결망에 반영되지 않으면 LLM Wiki로 확장되지 않는다.
- 자연어 조건을 단순 키워드 검색으로만 처리하면 "소음이 없는", "조용한", "저소음" 같은 표현을 같은 개념으로 다루기 어렵다.

## 3. 프로젝트 목표

MVP 목표는 다음과 같다.

- 첫 화면을 ChatGPT처럼 검색창 중심으로 만든다.
- 메뉴에서 임장 등록, 아파트 찾기, 지도 탐색, Wiki 문서, 후보 비교를 제공한다.
- 전국 합성 Wiki Page 10,000개로 지식 연결망을 충분히 채운다.
- 대한민국 지도에서 시도를 클릭하면 해당 지역의 Obsidian식 부분 그래프를 펼친다.
- 자연어 질문을 온톨로지 term으로 정규화하고 후보 매물을 추천한다.
- 새 Page 작성 시 온톨로지 연결이 자동 생성되도록 한다.

## 4. 의사결정 라운드

| Round | Question | Decision | Rationale | Impact |
| --- | --- | --- | --- | --- |
| 1 | 강의 주제 자체를 Wiki로 만들 것인가? | 부동산 임장 Wiki로 변경 | 실제 생활 문제라 MCP Tool 필요성이 더 명확하다. | 도메인 차별성과 데모 설득력이 높아진다. |
| 2 | 잠실 예시만 유지할 것인가? | 전국 10,000개 생성 Page로 확장 | 단일 지역은 그래프 밀도와 지역 탐색을 보여주기 어렵다. | 전국 지도, 시도별 그래프, 지역 특성 추천이 가능해진다. |
| 3 | 전체 그래프를 한 번에 보여줄 것인가? | 지도 선택 후 부분 그래프만 표시 | 전체 10,000개 node는 시각적으로 혼란스럽다. | Obsidian식 탐색감을 유지하면서 UI가 정돈된다. |
| 4 | 첫 화면에 비교표와 패널을 둘 것인가? | 검색창 하나를 중심으로 시작 | 사용자는 먼저 질문하고 이후 메뉴에서 기능을 고른다. | ChatGPT식 첫 경험을 제공한다. |
| 5 | 자연어 검색을 단순 키워드로 처리할 것인가? | ontology term 추출과 alias 정규화 적용 | "조용한", "소음 없는", "저소음"을 같은 개념으로 연결해야 한다. | 추천 이유와 ontology path를 설명할 수 있다. |
| 6 | 새 Page 작성 시 연결을 수동으로만 할 것인가? | 본문/태그에서 ontology term을 자동 추출 | 추가 글이 연결망을 자동으로 빽빽하게 만든다. | LLM Wiki가 시간이 지날수록 확장된다. |
| 7 | 후보 비교 기능을 제거할 것인가? | 첫 화면에서는 숨기고 메뉴 안에 유지 | 비교 기능은 유용하지만 초기 화면의 집중도를 깨뜨린다. | 요구사항을 만족하면서 기존 기능도 보존한다. |
| 8 | 실제 LLM API를 필수로 둘 것인가? | 결정론적 온톨로지 엔진으로 구현 | 제출/실행 환경에서 API 키 없이 동작해야 한다. | 로컬에서 안정적으로 검증 가능하다. |

## 5. 핵심 사용자 시나리오

### 시나리오 A: 검색으로 시작

1. 사용자가 첫 화면 검색창에 "소음이 없는 서울에 있는 집 찾아줘"를 입력한다.
2. `recommend_properties`가 `서울특별시`, `low_noise`를 추출한다.
3. 서울 지역의 후보 매물과 ontology path가 표시된다.
4. UI는 관련 지역 그래프를 내부적으로 로드해 사용자가 지도 탐색으로 이어갈 수 있게 한다.

### 시나리오 B: 지도에서 지역 그래프 탐색

1. 사용자가 메뉴에서 `지도 탐색`을 연다.
2. 대한민국 지도에서 `서울특별시`를 클릭한다.
3. `get_scoped_graph(province="서울특별시")`가 지역, ontology, 매물, 노트 node를 반환한다.
4. 화면은 해당 지역만 Obsidian식 그래프로 표시한다.

### 시나리오 C: 임장 글 등록

1. 사용자가 메뉴에서 `임장 등록하기`를 연다.
2. 제목, 지역, 본문, 태그를 입력하고 저장한다.
3. `create_page(confirmed=true)`가 본문/태그에서 ontology term을 추출한다.
4. 새 Page의 `ontology_terms`, `tags`, `related_pages`가 자동 보강된다.

### 시나리오 D: 후보 비교

1. 사용자가 메뉴에서 `후보 비교`를 연다.
2. 비교할 매물 Page를 선택한다.
3. `compare_properties`가 항목별 비교표를 반환한다.
4. Agent는 계약 추천이 아닌 정보 비교로만 응답한다.

## 6. 기능 요구사항

| ID | 기능 | 설명 | 우선순위 |
| --- | --- | --- | --- |
| FR-1 | 검색 중심 첫 화면 | 첫 진입 화면은 중앙 검색창 중심으로 구성 | Must |
| FR-2 | 메뉴 기반 기능 이동 | 지도 탐색, 아파트 찾기, 임장 등록, Wiki 문서, 후보 비교 제공 | Must |
| FR-3 | 전국 샘플 생성 | 10,000개 generated Wiki Page 생성 | Must |
| FR-4 | Atlas 조회 | 시도별 Page 수, 매물 수, 대표 ontology 반환 | Must |
| FR-5 | 지역 부분 그래프 | 시도/시군구 기준 node/edge 반환 | Must |
| FR-6 | 자연어 온톨로지 추출 | 질문과 본문에서 ontology term 추출 | Must |
| FR-7 | 후보 매물 추천 | 지역과 ontology 조건으로 매물 추천 | Must |
| FR-8 | Wiki Page 검색 | 키워드, 태그, 타입, 지역 기준 검색 | Must |
| FR-9 | Wiki Page 생성 | 승인 후 Markdown Page 저장 | Must |
| FR-10 | 자동 ontology 연결 | 생성/수정 시 `ontology_terms`와 관련 Page 자동 연결 | Must |
| FR-11 | Wiki Page 수정 | 승인 후 기존 Page 수정 | Should |
| FR-12 | 후보 비교 | 메뉴 내부에서 매물 비교표 제공 | Should |
| FR-13 | 실거래 조회 | API 키 있으면 공공데이터, 없으면 샘플 반환 | Could |

## 7. 비기능 요구사항

| 구분 | 요구사항 |
| --- | --- |
| 성능 | 첫 화면 진입 시 전체 10,000개 그래프를 로드하지 않는다. |
| 안정성 | 외부 API 키가 없어도 샘플 데이터로 동작한다. |
| 추적성 | UI와 Tool 응답에 사용 Tool, 정규화된 term, 근거 Page를 표시한다. |
| 확장성 | 새 Page가 추가될 때 ontology 연결망이 자동으로 확장된다. |
| 안전성 | 투자 추천, 계약 판단, 법률/세금 자문은 제공하지 않는다. |
| 개인정보 | 상세 주소, 전화번호, 소유자 정보 저장을 피한다. |

## 8. MCP Tool 명세

| Tool | 입력 | 출력 | 사용 Agent |
| --- | --- | --- | --- |
| `list_pages` | `type?`, `tag?`, `province?`, `district?`, `limit?` | Page metadata list | Wiki Search Agent |
| `get_page` | `page_id` 또는 `slug` | Page metadata + body | Wiki Search Agent |
| `search_pages` | `query`, `type?`, `tags?`, `province?`, `district?`, `limit?` | 검색 결과 | Wiki Search Agent |
| `get_related_pages` | `page_id` | 연결 Page 목록 | Wiki Search Agent |
| `get_atlas` | 없음 | 전국 시도 요약 | Atlas Agent |
| `get_scoped_graph` | `province?`, `district?`, `limit?` | 부분 그래프 | Atlas Agent |
| `extract_ontology_terms` | `text` | ontology term 목록 | Ontology Agent |
| `recommend_properties` | `query`, `province?`, `district?`, `limit?` | 추천 매물과 ontology path | Property Finder Agent |
| `create_field_note` | `raw_note`, `visited_at`, `region?`, `property?` | 임장 노트 초안 | Field Note Editor Agent |
| `create_page` | `title`, `type`, `body`, `tags?`, `related_pages?`, `metadata?`, `confirmed?` | 새 Page 초안 또는 저장 결과 | Wiki Writer Agent |
| `update_page` | `page_id`, `title?`, `body?`, `tags?`, `related_pages?`, `confirmed?` | 수정 초안 또는 저장 결과 | Wiki Writer Agent |
| `compare_properties` | `property_page_ids` | 비교표와 리스크 요약 | Property Comparison Agent |
| `fetch_apt_trade` | `lawd_cd`, `deal_ymd` | 매매 실거래 목록 | Data Retrieval Agent |
| `fetch_apt_rent` | `lawd_cd`, `deal_ymd` | 전월세 실거래 목록 | Data Retrieval Agent |

## 9. 외부 API 연동

| API | 용도 | URL |
| --- | --- | --- |
| 국토교통부_아파트 매매 실거래가 자료 | 지역 코드와 계약월 기준 매매 실거래 조회 | https://www.data.go.kr/data/15126469/openapi.do |
| 국토교통부_아파트 전월세 실거래가 자료 | 지역 코드와 계약월 기준 전월세 실거래 조회 | https://www.data.go.kr/data/15126474/openapi.do |

`serviceKey`가 없거나 호출에 실패하면 `source="sample_data"`와 fallback 사유를 반환한다.

## 10. MVP 화면 요구사항

- 첫 화면은 검색창 중심이다.
- 상단 메뉴 버튼으로 기능에 진입한다.
- 지도 탐색 화면은 대한민국 지도와 지역 그래프를 함께 보여준다.
- 아파트 찾기 화면은 검색어, 정규화된 ontology term, 추천 후보, 추천 이유를 보여준다.
- 임장 등록 화면은 새 Page 작성 후 자동 연결 결과를 보여준다.
- 후보 비교는 메뉴 내부에서만 접근한다.
- 사용된 Tool 이름이 화면에 표시된다.

## 11. 수용 기준

| ID | 기준 |
| --- | --- |
| AC-1 | `DOMAIN.md`, `PRD.md`, `README.md`, `AGENT_SPEC.md`, `mvp.png`가 제출 폴더에 존재한다. |
| AC-2 | `wiki/generated`에 Markdown Page 10,000개가 생성된다. |
| AC-3 | `get_atlas`가 전국 시도 요약을 반환한다. |
| AC-4 | `get_scoped_graph(province="서울특별시")`가 서울 부분 그래프를 반환한다. |
| AC-5 | 첫 화면은 검색창 중심이며 후보 비교가 노출되지 않는다. |
| AC-6 | `recommend_properties("소음이 없는 서울에 있는 집 찾아줘")`가 `서울특별시`, `low_noise`, 후보 매물을 반환한다. |
| AC-7 | `create_page(..., confirmed=true)`가 새 Page를 저장하고 ontology term을 자동 연결한다. |
| AC-8 | README가 MCP Tool 목록, HTTP API, 실행 방법, 검증 방법을 포함한다. |
| AC-9 | Agent SPEC이 Agent별 권한과 금지 기능을 포함한다. |
| AC-10 | 외부 API 실패 또는 API 키 부재 상황의 fallback 정책이 문서화된다. |

## 12. 테스트 및 검증 시나리오

| Test ID | 시나리오 | 입력 | 기대 결과 |
| --- | --- | --- | --- |
| T-1 | generated Page 수 확인 | `find wiki/generated -type f -name '*.md' | wc -l` | `10000` |
| T-2 | Atlas 조회 | `get_atlas()` | 17개 시도 요약 반환 |
| T-3 | 서울 그래프 조회 | `get_scoped_graph(province="서울특별시")` | 서울 node/edge 반환 |
| T-4 | 자연어 추천 | `recommend_properties("소음이 없는 서울에 있는 집 찾아줘")` | `low_noise`, 서울 후보 매물 반환 |
| T-5 | Wiki 검색 | `search_pages(query="서울 저소음", province="서울특별시")` | 관련 매물/ontology/Page 반환 |
| T-6 | Page 상세 조회 | `get_page("kr-property-00002")` | metadata와 본문 반환 |
| T-7 | Page 생성 | `create_page(..., confirmed=true)` | 파일 저장, ontology 연결 반영 |
| T-8 | Page 수정 초안 | `update_page(..., confirmed=false)` | 파일을 쓰지 않고 초안 반환 |
| T-9 | 후보 비교 | `compare_properties([...])` | 비교표 반환, 계약 추천 문구 없음 |
| T-10 | API 키 없음 | `.env`에 key 없음 | `source="sample_data"` fallback 반환 |

## 13. 리스크와 완화책

| 리스크 | 영향 | 완화책 |
| --- | --- | --- |
| 10,000개 그래프 과밀 | 화면 혼란과 성능 저하 | 지역 단위 scoped graph 사용 |
| 생성 데이터 오해 | 실제 매물로 착각 가능 | README와 UI에 합성 데이터임을 명시 |
| API 키 부재 | 실거래 조회 실패 | 샘플 fallback 제공 |
| Agent의 계약 판단 | 사용자 피해 가능성 | 투자/법률/계약 추천 금지 |
| 자동 ontology 오류 | 부정확한 연결 가능 | alias 목록과 metadata를 함께 노출해 검토 가능하게 함 |

## 14. Out of Scope

- 실시간 매물 크롤링
- 실제 지도 API와 경로 분석
- 투자 수익률 예측
- 대출 가능 금액 계산
- 세금 계산
- 등기부등본 자동 분석
- 자동 계약서 작성
- 개인정보 기반 맞춤 추천
