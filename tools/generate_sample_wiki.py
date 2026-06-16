from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED_ROOT = ROOT / "wiki" / "generated"
UPDATED_AT = "2026-06-16"

ONTOLOGY_TERMS = [
    ("low_noise", "저소음", ["조용한 골목", "대로변 이격", "방음 확인"]),
    ("station_access", "역 접근성", ["도보권 역", "환승 접근", "버스 대체"]),
    ("sunlight", "채광", ["남향", "앞 동 간격", "일조 시간"]),
    ("safety", "야간 안전", ["밝은 골목", "유동인구", "CCTV"]),
    ("green_access", "녹지 접근성", ["공원", "하천", "산책로"]),
    ("river_access", "수변 접근성", ["한강", "해변", "호수"]),
    ("school_district", "교육 인프라", ["학교", "학원가", "도서관"]),
    ("office_access", "직주근접", ["업무지구", "산단", "출퇴근"]),
    ("low_rent", "비용 접근성", ["월세 낮음", "관리비 낮음", "보증금 접근성"]),
    ("new_building", "신축/준신축", ["준공연도", "공용부", "단열"]),
    ("pet_friendly", "반려동물", ["산책", "펫 가능", "동물병원"]),
    ("parking", "주차", ["주차장", "세대당 주차", "자차 이동"]),
]

PROVINCES = [
    {
        "name": "서울특별시",
        "slug": "seoul",
        "target": 25,
        "districts": [
            "강남구",
            "서초구",
            "송파구",
            "마포구",
            "용산구",
            "성동구",
            "광진구",
            "중구",
            "종로구",
            "영등포구",
            "동작구",
            "관악구",
            "서대문구",
            "은평구",
            "강동구",
            "강서구",
            "양천구",
            "구로구",
            "금천구",
            "노원구",
            "도봉구",
            "강북구",
            "중랑구",
            "동대문구",
            "성북구",
        ],
        "features": ["직주근접", "지하철", "한강", "학군", "도심 생활"],
        "risk": "대로변 소음과 관리비 편차",
    },
    {
        "name": "부산광역시",
        "slug": "busan",
        "target": 16,
        "districts": ["해운대구", "수영구", "남구", "동래구", "부산진구", "연제구", "금정구", "북구", "사하구", "사상구", "강서구", "기장군", "중구", "서구", "동구", "영도구"],
        "features": ["해변", "항만", "산복도로", "도시철도", "관광"],
        "risk": "해안가 습기와 언덕 동선",
    },
    {"name": "대구광역시", "slug": "daegu", "target": 9, "districts": ["수성구", "중구", "동구", "서구", "남구", "북구", "달서구", "달성군", "군위군"], "features": ["분지", "학군", "산업", "도시철도"], "risk": "여름 열감과 대로변 소음"},
    {"name": "인천광역시", "slug": "incheon", "target": 10, "districts": ["연수구", "남동구", "부평구", "계양구", "미추홀구", "서구", "중구", "동구", "강화군", "옹진군"], "features": ["공항", "항만", "신도시", "수변", "광역철도"], "risk": "항공 소음과 출퇴근 거리"},
    {"name": "광주광역시", "slug": "gwangju", "target": 5, "districts": ["동구", "서구", "남구", "북구", "광산구"], "features": ["교육", "문화", "상무지구", "하천"], "risk": "권역별 대중교통 편차"},
    {"name": "대전광역시", "slug": "daejeon", "target": 5, "districts": ["유성구", "서구", "중구", "동구", "대덕구"], "features": ["연구단지", "KTX", "공원", "대학"], "risk": "차량 의존 동선"},
    {"name": "울산광역시", "slug": "ulsan", "target": 5, "districts": ["남구", "중구", "동구", "북구", "울주군"], "features": ["산업단지", "해안", "태화강", "자차"], "risk": "산단 인접 소음과 냄새"},
    {"name": "세종특별자치시", "slug": "sejong", "target": 7, "districts": ["나성동", "도담동", "어진동", "아름동", "고운동", "조치원읍", "금남면"], "features": ["행정중심", "신축", "공원", "자전거"], "risk": "상권 성숙도와 차량 동선"},
    {
        "name": "경기도",
        "slug": "gyeonggi",
        "target": 35,
        "districts": ["수원시", "성남시", "용인시", "고양시", "화성시", "부천시", "남양주시", "안산시", "평택시", "안양시", "시흥시", "파주시", "김포시", "의정부시", "광주시", "광명시", "군포시", "하남시", "오산시", "양주시", "이천시", "구리시", "안성시", "포천시", "의왕시", "여주시", "동두천시", "과천시", "가평군", "양평군", "연천군"],
        "features": ["광역교통", "신도시", "산단", "공원", "자차"],
        "risk": "출퇴근 시간과 역 접근성 편차",
    },
    {"name": "강원특별자치도", "slug": "gangwon", "target": 20, "districts": ["춘천시", "원주시", "강릉시", "동해시", "태백시", "속초시", "삼척시", "홍천군", "횡성군", "영월군", "평창군", "정선군", "철원군", "화천군", "양구군", "인제군", "고성군", "양양군"], "features": ["산", "호수", "해안", "관광", "저밀도"], "risk": "겨울 이동성과 대중교통 배차"},
    {"name": "충청북도", "slug": "chungbuk", "target": 11, "districts": ["청주시", "충주시", "제천시", "보은군", "옥천군", "영동군", "증평군", "진천군", "괴산군", "음성군", "단양군"], "features": ["내륙", "산업", "대학", "호수"], "risk": "권역별 생활편의 격차"},
    {"name": "충청남도", "slug": "chungnam", "target": 17, "districts": ["천안시", "아산시", "서산시", "당진시", "공주시", "보령시", "논산시", "계룡시", "금산군", "부여군", "서천군", "청양군", "홍성군", "예산군", "태안군"], "features": ["산단", "서해안", "KTX", "신도시"], "risk": "차량 의존과 산단 인접성"},
    {"name": "전북특별자치도", "slug": "jeonbuk", "target": 14, "districts": ["전주시", "군산시", "익산시", "정읍시", "남원시", "김제시", "완주군", "진안군", "무주군", "장수군", "임실군", "순창군", "고창군", "부안군"], "features": ["전통도심", "산업", "농촌", "관광"], "risk": "노후 주택과 배차 간격"},
    {"name": "전라남도", "slug": "jeonnam", "target": 22, "districts": ["목포시", "여수시", "순천시", "나주시", "광양시", "담양군", "곡성군", "구례군", "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군", "영암군", "무안군", "함평군", "영광군", "장성군", "완도군", "진도군", "신안군"], "features": ["해안", "산단", "농어촌", "관광"], "risk": "해풍 습기와 생활권 거리"},
    {"name": "경상북도", "slug": "gyeongbuk", "target": 22, "districts": ["포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시", "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군", "울진군", "울릉군"], "features": ["산단", "대학", "역사", "해안"], "risk": "도심 간 이동 거리"},
    {"name": "경상남도", "slug": "gyeongnam", "target": 20, "districts": ["창원시", "진주시", "통영시", "사천시", "김해시", "밀양시", "거제시", "양산시", "의령군", "함안군", "창녕군", "고성군", "남해군", "하동군", "산청군", "함양군", "거창군", "합천군"], "features": ["조선", "기계산업", "남해안", "신도시"], "risk": "산단 교대 소음과 차량 동선"},
    {"name": "제주특별자치도", "slug": "jeju", "target": 7, "districts": ["제주시", "서귀포시", "애월읍", "조천읍", "한림읍"], "features": ["해변", "관광", "자연", "저층"], "risk": "바람, 습기, 차량 의존"},
]

PROPERTY_PATTERNS = [
    ("역세권 소형 아파트", "전용 59㎡", ["station_access", "office_access"], ["도보 6분", "환승 접근 양호"]),
    ("저소음 주거 블록", "전용 74㎡", ["low_noise", "safety"], ["대로변 이격", "야간 조도 양호"]),
    ("공원 인접 중형 아파트", "전용 84㎡", ["green_access", "pet_friendly"], ["산책로 접근", "반려동물 동선"]),
    ("신축 오피스텔", "전용 39㎡", ["new_building", "office_access"], ["공용부 깔끔", "직주근접"]),
    ("학군 생활권 아파트", "전용 84㎡", ["school_district", "sunlight"], ["학교 접근", "남향 위주"]),
    ("수변 조망 주거", "전용 59㎡", ["river_access", "sunlight"], ["수변 산책", "조망 확인"]),
    ("비용 절약형 빌라", "전용 49㎡", ["low_rent", "station_access"], ["월세 접근성", "역까지 버스 가능"]),
    ("주차 여유 단지", "전용 84㎡", ["parking", "safety"], ["자차 이용", "단지 내 조도"]),
]


def slugify(value: str) -> str:
    import re

    value = value.strip().lower()
    value = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def normalize_districts() -> list[dict[str, str]]:
    districts: list[dict[str, str]] = []
    for province in PROVINCES:
        names = list(province["districts"])
        while len(names) < province["target"]:
            names.append(f"{province['name'].replace('특별자치도', '').replace('광역시', '').replace('특별시', '')} 생활권 {len(names) + 1:02d}")
        for name in names[: province["target"]]:
            districts.append(
                {
                    "province": province["name"],
                    "province_slug": province["slug"],
                    "district": name,
                    "district_slug": slugify(name),
                    "features": province["features"],
                    "risk": province["risk"],
                }
            )
    if len(districts) != 250:
        raise RuntimeError(f"Expected 250 districts, got {len(districts)}")
    return districts


DISTRICTS = normalize_districts()


def page_id(kind: str, index: int) -> str:
    return f"kr-{kind}-{index:05d}"


def ontology_id(index: int) -> str:
    return page_id("ontology", index)


def region_id(index: int) -> str:
    return page_id("region", index)


def property_id(index: int) -> str:
    return page_id("property", index)


def note_id(index: int) -> str:
    return page_id("field-note", index)


def checklist_id(index: int) -> str:
    return page_id("checklist", index)


def trade_id(index: int) -> str:
    return page_id("trade-summary", index)


def render_page(
    page_id_value: str,
    title: str,
    page_type: str,
    tags: list[str],
    source: str,
    related_pages: list[str],
    body: str,
    metadata: dict,
) -> str:
    lines = [
        "---",
        f"id: {page_id_value}",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"type: {page_type}",
        f"tags: {json.dumps(tags, ensure_ascii=False)}",
        f"source: {json.dumps(source, ensure_ascii=False)}",
        f"updated_at: {UPDATED_AT}",
        f"related_pages: {json.dumps(related_pages, ensure_ascii=False)}",
    ]
    for key, value in metadata.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.extend(["---", "", body.strip(), ""])
    return "\n".join(lines)


def write_page(relative_dir: str, page_id_value: str, markdown: str) -> None:
    target_dir = GENERATED_ROOT / relative_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"{page_id_value}.md").write_text(markdown, encoding="utf-8")


def term_label(term: str) -> str:
    return next(label for key, label, _ in ONTOLOGY_TERMS if key == term)


def province_term_ontology_id(province_index: int, term_index: int) -> str:
    return ontology_id((province_index - 1) * len(ONTOLOGY_TERMS) + term_index)


def district_region_page_id(district_index: int) -> str:
    return region_id(17 + district_index)


def generate_regions() -> int:
    count = 0
    for index, province in enumerate(PROVINCES, start=1):
        region_pages = [district_region_page_id(i + 1) for i, item in enumerate(DISTRICTS) if item["province"] == province["name"]][:14]
        ontology_pages = [province_term_ontology_id(index, term_index) for term_index in range(1, len(ONTOLOGY_TERMS) + 1)]
        body = f"""# {province['name']} 임장 지도

## 지역 특징
- 대표 생활 특성: {", ".join(province["features"])}
- 주요 확인 리스크: {province["risk"]}

## 탐색 방법
- 시군구 Page를 열면 해당 지역 매물과 온톨로지 개념이 연결된다.
- 추천 Agent는 사용자의 자연어 질문을 지역어와 온톨로지 단어로 정규화한다.
"""
        write_page(
            "regions",
            region_id(index),
            render_page(
                region_id(index),
                f"{province['name']} 임장 지도",
                "region",
                ["generated", "province", province["slug"]],
                "generated_national_ontology_sample",
                region_pages + ontology_pages[:4],
                body,
                {
                    "province": province["name"],
                    "district": "",
                    "ontology_terms": [term for term, *_ in ONTOLOGY_TERMS[:6]],
                    "features": province["features"],
                    "description": f"{province['name']} 전체 생활권 요약",
                    "lat_lng": [36.5 + index * 0.05, 127.5 + index * 0.04],
                },
            ),
        )
        count += 1

    for district_index, district in enumerate(DISTRICTS, start=1):
        province_index = next(i for i, province in enumerate(PROVINCES, start=1) if province["name"] == district["province"])
        property_start = (district_index - 1) * 24 + 1
        property_links = [property_id(property_start + offset) for offset in range(8)]
        terms = [ONTOLOGY_TERMS[(district_index + offset) % len(ONTOLOGY_TERMS)][0] for offset in range(4)]
        related = [region_id(province_index)] + property_links + [province_term_ontology_id(province_index, ((district_index + offset) % len(ONTOLOGY_TERMS)) + 1) for offset in range(3)]
        body = f"""# {district['province']} {district['district']} 생활권

## 지역 특징
- 이 생활권은 {", ".join(district["features"][:3])} 요소가 강한 임장 후보지다.
- 확인 리스크: {district["risk"]}

## 온톨로지 연결
- 주요 개념: {", ".join(term_label(term) for term in terms)}
- 매물 Page는 소음, 교통, 채광, 안전, 비용 단어와 자동 연결된다.
"""
        write_page(
            "regions",
            district_region_page_id(district_index),
            render_page(
                district_region_page_id(district_index),
                f"{district['province']} {district['district']} 생활권",
                "region",
                ["generated", "district", district["province_slug"], district["district_slug"]],
                "generated_national_ontology_sample",
                related,
                body,
                {
                    "province": district["province"],
                    "district": district["district"],
                    "ontology_terms": terms,
                    "features": district["features"],
                    "description": f"{district['district']} 생활권 임장 요약",
                    "lat_lng": [33.5 + (district_index % 80) * 0.07, 126.0 + (district_index % 60) * 0.08],
                },
            ),
        )
        count += 1
    return count


def generate_ontology_pages() -> int:
    count = 0
    for province_index, province in enumerate(PROVINCES, start=1):
        for term_index, (term, label, aliases) in enumerate(ONTOLOGY_TERMS, start=1):
            oid = province_term_ontology_id(province_index, term_index)
            related = [region_id(province_index)]
            related += [property_id(((province_index - 1) * 24 + term_index + offset * 17 - 1) % 6000 + 1) for offset in range(8)]
            body = f"""# {province['name']} {label} 온톨로지

## 정규화 단어
- 대표 개념: {term}
- 연결 표현: {", ".join(aliases)}

## Agent 사용
- 사용자가 이 표현을 질문하면 관련 매물의 `ontology_terms`와 점수를 비교한다.
- 추천 결과에는 이 온톨로지 Page와 후보 매물의 연결 경로가 표시된다.
"""
            write_page(
                "ontology",
                oid,
                render_page(
                    oid,
                    f"{province['name']} {label} 온톨로지",
                    "ontology",
                    ["generated", "ontology", province["slug"], term],
                    "generated_national_ontology_sample",
                    related,
                    body,
                    {
                        "province": province["name"],
                        "district": "",
                        "ontology_terms": [term],
                        "features": aliases,
                        "description": f"{label} 조건을 {province['name']} 매물에 연결",
                    },
                ),
            )
            count += 1

    for extra_index in range(205, 501):
        district = DISTRICTS[(extra_index - 205) % len(DISTRICTS)]
        term, label, aliases = ONTOLOGY_TERMS[(extra_index - 205) % len(ONTOLOGY_TERMS)]
        related = [district_region_page_id((extra_index - 205) % len(DISTRICTS) + 1)]
        related += [property_id((extra_index * 11 + offset * 23) % 6000 + 1) for offset in range(6)]
        body = f"""# {district['district']} {label} 세부 개념

## 지역 문맥
- {district['province']} {district['district']}에서 {label} 조건을 판단할 때 쓰는 연결 개념이다.
- 관련 표현: {", ".join(aliases)}

## 자동 연결
- 새 임장 글에 관련 단어가 들어오면 이 개념과 같은 ontology term으로 묶인다.
"""
        write_page(
            "ontology",
            ontology_id(extra_index),
            render_page(
                ontology_id(extra_index),
                f"{district['district']} {label} 세부 개념",
                "ontology",
                ["generated", "ontology", district["province_slug"], district["district_slug"], term],
                "generated_national_ontology_sample",
                related,
                body,
                {
                    "province": district["province"],
                    "district": district["district"],
                    "ontology_terms": [term],
                    "features": aliases,
                    "description": f"{district['district']} {label} 조건",
                },
            ),
        )
        count += 1
    return count


def property_terms(index: int, district: dict[str, str]) -> list[str]:
    pattern_terms = PROPERTY_PATTERNS[(index - 1) % len(PROPERTY_PATTERNS)][2]
    bonus = "low_noise" if district["province"] == "서울특별시" and index % 3 == 0 else ONTOLOGY_TERMS[index % len(ONTOLOGY_TERMS)][0]
    return list(dict.fromkeys(pattern_terms + [bonus]))


def generate_properties() -> int:
    count = 0
    for index in range(1, 6001):
        district_index = ((index - 1) // 24) + 1
        district = DISTRICTS[district_index - 1]
        province_index = next(i for i, province in enumerate(PROVINCES, start=1) if province["name"] == district["province"])
        title, area, pattern_terms, observations = PROPERTY_PATTERNS[(index - 1) % len(PROPERTY_PATTERNS)]
        terms = property_terms(index, district)
        deposit = 18000 + (index % 97) * 650
        rent = 35 + (index % 13) * 6
        management = 7 + (index % 9)
        floor_noise = "조용한 이면도로" if "low_noise" in terms else "대로변 소음 시간대 확인"
        related = [
            region_id(province_index),
            district_region_page_id(district_index),
            checklist_id(((district_index - 1) % 200) + 1),
        ]
        related += [province_term_ontology_id(province_index, [term for term, *_ in ONTOLOGY_TERMS].index(term) + 1) for term in terms[:3]]
        if index <= 3000:
            related.append(note_id(index))
        body = f"""# {district['province']} {district['district']} 후보 {index:04d}: {title}

## 기본 정보
- 지역: {district['province']} {district['district']}
- 면적: {area}
- 보증금: {deposit:,}만원
- 월세: {rent}만원
- 관리비: {management}만원

## 현장 관찰
- 특징: {", ".join(district["features"][:3])}
- 관찰: {", ".join(observations)}
- 소음: {floor_noise}
- 교통: 역 또는 중심 정류장 접근성은 임장 노트와 함께 확인

## 온톨로지 단어
- {", ".join(term_label(term) for term in terms)}

## 확인 필요
- 실제 가격, 관리비, 계약 조건은 공인 자료로 재확인
- 본 Page는 MVP 검증용 합성 샘플이며 계약 추천이 아니다.
"""
        scores = {term: 5 + ((index + offset) % 6) for offset, term in enumerate(terms)}
        if "low_noise" in terms:
            scores["low_noise"] = 11 if district["province"] == "서울특별시" else 9
        write_page(
            "properties",
            property_id(index),
            render_page(
                property_id(index),
                f"{district['province']} {district['district']} 후보 {index:04d} {title}",
                "property",
                ["generated", "property", district["province_slug"], district["district_slug"]] + terms,
                "generated_national_ontology_sample",
                related,
                body,
                {
                    "province": district["province"],
                    "district": district["district"],
                    "ontology_terms": terms,
                    "features": district["features"] + observations,
                    "scores": scores,
                    "description": f"{district['district']} {title}",
                    "lat_lng": [33.0 + (index % 90) * 0.075, 126.0 + (index % 70) * 0.08],
                },
            ),
        )
        count += 1
    return count


def generate_notes() -> int:
    count = 0
    observations = [
        "창문을 닫으면 외부 소음이 크게 줄어드는 편이었다.",
        "역까지 가는 길은 평지지만 횡단보도 대기 시간이 있었다.",
        "공용부 조명은 밝고 택배 보관 공간은 보통이었다.",
        "주변 상권은 충분하지만 심야 유동인구는 시간대별 확인이 필요하다.",
        "채광은 양호했으나 앞 건물과의 간격은 다시 확인해야 한다.",
        "주차 진입로가 좁아 자차 이용자는 재방문 확인이 필요하다.",
    ]
    for index in range(1, 3001):
        property_index = index
        district_index = ((property_index - 1) // 24) + 1
        district = DISTRICTS[district_index - 1]
        terms = property_terms(property_index, district)
        body = f"""# {district['district']} 후보 {property_index:04d} 임장 노트

## 관찰 내용
- {observations[index % len(observations)]}
- {observations[(index + 2) % len(observations)]}
- 지역 특성: {", ".join(district["features"][:3])}

## 온톨로지화
- 연결 단어: {", ".join(term_label(term) for term in terms)}
- 새 글 등록 시 같은 의미 단어는 동일 ontology term으로 묶인다.

## 확인 필요
- 현장 관찰 기록이며 투자 또는 계약 추천이 아니다.
"""
        write_page(
            "notes",
            note_id(index),
            render_page(
                note_id(index),
                f"{district['district']} 후보 {property_index:04d} 임장 노트",
                "field_note",
                ["generated", "field-note", district["province_slug"], district["district_slug"]] + terms,
                "generated_national_ontology_sample",
                [property_id(property_index), district_region_page_id(district_index)] + [province_term_ontology_id(next(i for i, province in enumerate(PROVINCES, start=1) if province["name"] == district["province"]), [term for term, *_ in ONTOLOGY_TERMS].index(term) + 1) for term in terms[:2]],
                body,
                {
                    "province": district["province"],
                    "district": district["district"],
                    "ontology_terms": terms,
                    "features": district["features"],
                    "description": f"{property_index:04d}번 후보 현장 관찰",
                },
            ),
        )
        count += 1
    return count


def generate_checklists() -> int:
    count = 0
    for index in range(1, 201):
        district = DISTRICTS[index - 1]
        terms = [ONTOLOGY_TERMS[(index + offset) % len(ONTOLOGY_TERMS)][0] for offset in range(4)]
        body = f"""# {district['district']} 임장 체크리스트

## 확인 항목
- 소음: 평일 낮, 주말, 야간을 분리해서 기록한다.
- 교통: 실제 도보 시간과 대체 버스 노선을 함께 기록한다.
- 채광: 창 방향과 앞 동 거리를 사진 메모로 남긴다.
- 안전: 야간 조도와 귀가 동선을 확인한다.

## 지역 문맥
- {district['province']} {district['district']} 특성: {", ".join(district["features"][:3])}
"""
        write_page(
            "checklists",
            checklist_id(index),
            render_page(
                checklist_id(index),
                f"{district['district']} 임장 체크리스트",
                "checklist",
                ["generated", "checklist", district["province_slug"], district["district_slug"]],
                "generated_national_ontology_sample",
                [district_region_page_id(index)] + [property_id((index - 1) * 24 + offset + 1) for offset in range(6)],
                body,
                {
                    "province": district["province"],
                    "district": district["district"],
                    "ontology_terms": terms,
                    "features": district["features"],
                    "description": f"{district['district']} 현장 확인 기준",
                },
            ),
        )
        count += 1
    return count


def generate_trade_summaries() -> int:
    count = 0
    for index in range(1, 34):
        province = PROVINCES[(index - 1) % len(PROVINCES)]
        district = next(item for item in DISTRICTS if item["province"] == province["name"])
        median = 32000 + index * 2100
        body = f"""# {province['name']} 실거래 샘플 요약 {index:02d}

## 표본 요약
- 합성 중앙값: {median:,}만원
- 지역 특성: {", ".join(province["features"][:3])}

## 주의
- API 키가 없을 때 Viewer와 Agent 검증을 위한 샘플이다.
- 실제 계약 판단에는 공공데이터 원문 확인이 필요하다.
"""
        write_page(
            "data",
            trade_id(index),
            render_page(
                trade_id(index),
                f"{province['name']} 실거래 샘플 요약 {index:02d}",
                "trade_summary",
                ["generated", "trade-summary", province["slug"]],
                "generated_national_ontology_sample",
                [region_id((index - 1) % len(PROVINCES) + 1), district_region_page_id(DISTRICTS.index(district) + 1)] + [property_id(((index - 1) * 181 + offset) % 6000 + 1) for offset in range(8)],
                body,
                {
                    "province": province["name"],
                    "district": district["district"],
                    "ontology_terms": ["low_rent", "station_access"],
                    "features": province["features"],
                    "description": f"{province['name']} 거래 샘플",
                },
            ),
        )
        count += 1
    return count


def main() -> int:
    if GENERATED_ROOT.exists():
        shutil.rmtree(GENERATED_ROOT)
    counts = {
        "regions": generate_regions(),
        "ontology": generate_ontology_pages(),
        "properties": generate_properties(),
        "notes": generate_notes(),
        "checklists": generate_checklists(),
        "trade_summaries": generate_trade_summaries(),
    }
    total = sum(counts.values())
    if total != 10000:
        raise RuntimeError(f"Expected 10000 generated pages, got {total}")
    print(json.dumps({"generated_pages": total, "counts": counts}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
