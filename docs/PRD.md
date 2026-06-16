# PRD.md

# Real Estate Field Wiki PRD

## 1. 배경

부동산 매물을 비교할 때 사용자는 지역 정보, 매물 특징, 임장 메모, 실거래가, 체크리스트를 여러 앱과 문서에 나누어 저장한다. 이 방식은 정보가 분산되어 다시 찾기 어렵고, AI Agent가 답변을 만들 때 어떤 자료를 근거로 삼아야 하는지 명확하지 않다.

Real Estate Field Wiki는 이 문제를 해결하기 위해 부동산 임장 지식을 Wiki Page로 저장하고, MCP 서버가 Wiki 조회/검색/비교/실거래가 조회 기능을 Tool로 제공하는 프로젝트이다.

## 2. 문제 정의

사용자는 여러 매물을 비교할 때 다음 어려움을 겪는다.

- 임장 메모가 비정형 텍스트로 남아 다시 비교하기 어렵다.
- 지역, 매물, 체크리스트, 실거래가가 서로 연결되지 않는다.
- AI Agent가 사용자 메모와 외부 데이터를 구분하지 못하면 부정확한 답변을 만들 수 있다.
- 공공데이터 API는 직접 호출하기 번거롭고, 결과를 Wiki 지식과 함께 보기 어렵다.

## 3. 프로젝트 목표

MVP 목표는 **부동산 임장 기록과 매물 비교를 위한 Wiki Page를 서빙하고, AI Agent가 MCP Tool을 통해 Wiki와 실거래가 데이터를 안전하게 조회하도록 만드는 것**이다.

## 4. 의사결정 라운드

| Round | Question | Decision | Rationale | Impact |
| --- | --- | --- | --- | --- |
| 1 | 초기 후보인 강의 주제로 Wiki를 만들 것인가? | 부동산 임장 Wiki로 변경 | 강의 주제 자체보다 독립 생활 도메인이 Wiki Tool의 필요성을 더 명확하게 보여준다. | 도메인 문서와 MVP 화면의 차별성이 높아진다. |
| 2 | 부동산 전체를 다룰 것인가? | 임장 기록, 매물 비교, 아파트 실거래가로 범위 축소 | 부동산 전체는 세금, 대출, 법률, 투자 판단까지 확장되어 MVP 범위가 커진다. | 구현 가능성이 높고 Agent 권한 경계가 명확해진다. |
| 3 | 실제 API를 필수로 둘 것인가? | API 연동은 지원하되 샘플 데이터 fallback 제공 | 공공데이터 API는 활용신청과 serviceKey가 필요하므로 제출 환경에서 실패할 수 있다. | MVP는 안정적으로 동작하고 확장 가능성도 설명할 수 있다. |
| 4 | Agent가 Wiki Page를 직접 수정할 수 있는가? | 초안 생성은 허용, 삭제와 확정 수정은 금지 | 부동산 정보는 사용자 판단에 영향을 줄 수 있어 무제한 수정은 위험하다. | Agent SPEC에 권한과 승인 규칙을 명확히 기술한다. |
| 5 | GUI는 어떤 방식으로 보여줄 것인가? | Page 목록, Page 본문, 관련 Page, Tool 결과를 3열 화면으로 시각화 | Wiki Serving과 Tool 사용 결과를 한 화면에서 확인할 수 있다. | MVP PNG가 Wiki Serving 화면 증빙을 제공한다. |

## 5. 핵심 사용자 시나리오

### 시나리오 A: 임장 메모 정리

1. 사용자가 임장 중 작성한 텍스트 메모를 입력한다.
2. `create_field_note` Tool이 메모를 Wiki Page 초안으로 변환한다.
3. Field Note Editor Agent가 누락 항목을 표시한다.
4. 사용자는 초안을 확인한 뒤 Wiki Page로 저장한다.

### 시나리오 B: 매물 비교

1. 사용자가 비교할 매물 Page 2개 이상을 선택한다.
2. `compare_properties` Tool이 면적, 가격, 교통, 소음, 관리비, 리스크 항목을 비교한다.
3. Property Comparison Agent가 비교표와 확인 필요 사항을 요약한다.
4. Agent는 매수/임대 추천 대신 근거 기반 비교만 제공한다.

### 시나리오 C: 실거래가 조회

1. 사용자가 지역 코드와 계약월을 입력한다.
2. `fetch_apt_trade` 또는 `fetch_apt_rent` Tool이 공공데이터 API를 호출한다.
3. API 키가 없거나 실패하면 샘플 데이터를 반환하고 실패 사유를 표시한다.
4. 조회 결과는 선택한 매물 Page의 우측 패널에 표시된다.

## 6. 기능 요구사항

| ID | 기능 | 설명 | 우선순위 |
| --- | --- | --- | --- |
| FR-1 | Wiki Page 목록 조회 | Page 제목, 타입, 태그, 수정일을 반환 | Must |
| FR-2 | Wiki Page 상세 조회 | Page ID 또는 slug로 본문과 메타데이터를 반환 | Must |
| FR-3 | Wiki Page 검색 | 키워드, 태그, 타입 기준으로 검색 | Must |
| FR-4 | 관련 Page 조회 | 매물과 지역, 체크리스트, 임장 노트의 연결 관계 반환 | Must |
| FR-5 | 임장 메모 초안 생성 | 비정형 메모를 Wiki Page 초안으로 변환 | Should |
| FR-6 | 매물 비교 | 선택한 매물 Page를 기준 항목별로 비교 | Should |
| FR-7 | 매매 실거래가 조회 | 국토교통부 아파트 매매 실거래가 API 연동 | Could |
| FR-8 | 전월세 실거래가 조회 | 국토교통부 아파트 전월세 실거래가 API 연동 | Could |

## 7. 비기능 요구사항

| 구분 | 요구사항 |
| --- | --- |
| 안정성 | 외부 API 실패 시 GUI와 Agent 응답이 중단되지 않아야 한다. |
| 추적성 | Agent가 사용한 Tool 이름과 조회 기준을 응답에 남겨야 한다. |
| 보안 | 공공데이터 API serviceKey는 `.env`에 저장하고 문서나 로그에 노출하지 않는다. |
| 정확성 | 실거래가 데이터는 출처와 조회 기준을 함께 표시한다. |
| 제한성 | Agent는 투자 추천, 법률 자문, 세금 판단을 하지 않는다. |

## 8. MCP Tool 명세

| Tool | 입력 | 출력 | 사용 Agent |
| --- | --- | --- | --- |
| `list_pages` | `type?`, `tag?` | Page metadata list | Wiki Search Agent |
| `get_page` | `page_id` 또는 `slug` | Page metadata + markdown body | Wiki Search Agent |
| `search_pages` | `query`, `type?`, `tags?` | 검색 결과 목록 | Wiki Search Agent |
| `get_related_pages` | `page_id` | 관련 Page 목록 | Wiki Search Agent |
| `create_field_note` | `raw_note`, `visited_at`, `region?`, `property?` | Wiki Page 초안 | Field Note Editor Agent |
| `compare_properties` | `property_page_ids` | 비교표와 리스크 요약 | Property Comparison Agent |
| `fetch_apt_trade` | `lawd_cd`, `deal_ymd` | 매매 실거래 목록 | Data Retrieval Agent |
| `fetch_apt_rent` | `lawd_cd`, `deal_ymd` | 전월세 실거래 목록 | Data Retrieval Agent |

## 9. 외부 API 연동

MVP에서 사용할 수 있는 공식 API 후보는 다음과 같다.

| API | 용도 | URL |
| --- | --- | --- |
| 국토교통부_아파트 매매 실거래가 자료 | 지역 코드와 계약월 기준 매매 실거래 조회 | https://www.data.go.kr/data/15126469/openapi.do |
| 국토교통부_아파트 전월세 실거래가 자료 | 지역 코드와 계약월 기준 전월세 실거래 조회 | https://www.data.go.kr/data/15126474/openapi.do |

공통 요청 파라미터는 `serviceKey`, `LAWD_CD`, `DEAL_YMD`이다. `serviceKey`가 없는 경우 MVP는 샘플 JSON을 반환한다.

## 10. MVP 화면 요구사항

MVP GUI는 다음 요소를 포함한다.

- 상단 검색창
- 좌측 Wiki Page 목록
- 중앙 Wiki Page 상세 본문
- 우측 관련 Page와 MCP Tool 결과
- 하단 매물 비교 결과
- 현재 사용된 Tool 이름 표시

## 11. 수용 기준

| ID | 기준 |
| --- | --- |
| AC-1 | `DOMAIN.md`, `PRD.md`, `README.md`, `AGENT_SPEC.md`, `mvp.png`가 제출 폴더에 존재한다. |
| AC-2 | README가 MCP Tool 목록, 작동 방식, 실행 방법을 포함한다. |
| AC-3 | PRD가 의사결정 라운드 표를 포함한다. |
| AC-4 | Agent SPEC이 Agent별 권한과 금지 기능을 포함한다. |
| AC-5 | MVP 이미지가 Wiki Page Serving 화면과 Tool 결과 패널을 보여준다. |
| AC-6 | 각 MCP Tool의 입력, 출력, 사용 Agent가 문서에 명시된다. |
| AC-7 | 외부 API 실패 또는 API 키 부재 상황의 fallback 정책이 문서화된다. |
| AC-8 | Agent가 투자 추천, 법률 자문, 근거 없는 Page 생성 요청을 거절하는 규칙이 문서화된다. |

## 12. 테스트 및 검증 시나리오

| Test ID | 시나리오 | 입력 | 기대 결과 |
| --- | --- | --- | --- |
| T-1 | Wiki Page 목록 조회 | `list_pages(type="property")` | 매물 Page 목록과 태그가 반환된다. |
| T-2 | Page 상세 조회 | `get_page("property-jamsil-a")` | Page 메타데이터와 Markdown 본문이 반환된다. |
| T-3 | 키워드 검색 | `search_pages(query="잠실 전세 소음")` | 매물, 체크리스트, 임장 노트가 관련도 순으로 반환된다. |
| T-4 | 관련 Page 조회 | `get_related_pages("property-jamsil-a")` | 지역 Page, 체크리스트, 실거래 요약 Page가 반환된다. |
| T-5 | 임장 메모 초안 생성 | `create_field_note(raw_note=...)` | 제목, 태그, 확인 필요 항목이 포함된 Markdown 초안이 생성된다. |
| T-6 | 매물 비교 | `compare_properties(["property-jamsil-a", "property-jamsil-b"])` | 비교표와 리스크 요약이 반환되고 추천 문구는 포함되지 않는다. |
| T-7 | 실거래가 조회 성공 | `fetch_apt_rent(lawd_cd="11710", deal_ymd="202405")` | API 또는 샘플 데이터 출처와 함께 거래 항목이 반환된다. |
| T-8 | API 키 없음 | `.env`에 key 없음 | `source="sample_data"`와 fallback 사유가 반환된다. |
| T-9 | 금지 요청 처리 | "이 매물 사도 돼?" | Agent는 추천을 거절하고 비교표/체크리스트만 제공한다. |

## 13. 리스크와 완화책

| 리스크 | 영향 | 완화책 |
| --- | --- | --- |
| 공공데이터 API 키 미발급 | 실제 조회 실패 | 샘플 데이터 fallback 제공 |
| 부동산 정보의 법률/투자 오해 | 사용자 피해 가능성 | 투자 추천과 법률 자문 금지 |
| Agent의 근거 없는 답변 | 신뢰도 저하 | Wiki Page 또는 API 출처 없이는 단정 금지 |
| 도메인 범위 확대 | MVP 완성도 저하 | 임장, 매물 비교, 실거래 조회로 범위 제한 |

## 14. Out of Scope

- 실시간 매물 크롤링
- 지도 기반 경로 분석
- 투자 수익률 예측
- 대출 가능 금액 계산
- 세금 계산
- 등기부등본 자동 분석
- 자동 계약서 작성
