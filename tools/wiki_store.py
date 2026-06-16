from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, fields
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WIKI_DIR = ROOT / "wiki"
PAGE_TYPE_DIRS = {
    "region": "regions",
    "property": "properties",
    "field_note": "notes",
    "checklist": "checklists",
    "trade_summary": "data",
    "ontology": "ontology",
}

SUMMARY_METADATA_KEYS = [
    "province",
    "district",
    "lat_lng",
    "ontology_terms",
    "features",
    "scores",
    "description",
]

ONTOLOGY_ALIASES: dict[str, list[str]] = {
    "low_noise": ["소음 없는", "소음이 없는", "조용한", "저소음", "소음 적은", "방음", "대로변 아님"],
    "station_access": ["역세권", "역 가까운", "도보", "지하철", "교통 좋은"],
    "sunlight": ["채광", "햇빛", "남향", "밝은"],
    "safety": ["안전", "야간 안전", "골목 밝은", "치안"],
    "green_access": ["공원", "녹지", "산책", "숲", "하천"],
    "river_access": ["한강", "강변", "수변"],
    "school_district": ["학군", "학교", "학원가", "교육"],
    "office_access": ["직주근접", "업무지구", "출퇴근", "회사 가까운"],
    "low_rent": ["저렴한", "월세 낮은", "관리비 낮은", "가격 접근성"],
    "new_building": ["신축", "준신축", "새 아파트"],
    "pet_friendly": ["반려동물", "펫", "강아지", "고양이"],
    "parking": ["주차", "자차", "주차장"],
}

REGION_ALIASES: dict[str, str] = {
    "서울": "서울특별시",
    "서울특별시": "서울특별시",
    "부산": "부산광역시",
    "부산광역시": "부산광역시",
    "대구": "대구광역시",
    "대구광역시": "대구광역시",
    "인천": "인천광역시",
    "인천광역시": "인천광역시",
    "광주": "광주광역시",
    "광주광역시": "광주광역시",
    "대전": "대전광역시",
    "대전광역시": "대전광역시",
    "울산": "울산광역시",
    "울산광역시": "울산광역시",
    "세종": "세종특별자치시",
    "세종특별자치시": "세종특별자치시",
    "경기": "경기도",
    "경기도": "경기도",
    "강원": "강원특별자치도",
    "강원도": "강원특별자치도",
    "강원특별자치도": "강원특별자치도",
    "충북": "충청북도",
    "충청북도": "충청북도",
    "충남": "충청남도",
    "충청남도": "충청남도",
    "전북": "전북특별자치도",
    "전라북도": "전북특별자치도",
    "전북특별자치도": "전북특별자치도",
    "전남": "전라남도",
    "전라남도": "전라남도",
    "경북": "경상북도",
    "경상북도": "경상북도",
    "경남": "경상남도",
    "경상남도": "경상남도",
    "제주": "제주특별자치도",
    "제주도": "제주특별자치도",
    "제주특별자치도": "제주특별자치도",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "untitled"


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("\"'") for item in inner.split(",")]
    if raw.startswith("{") and raw.endswith("}"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw.strip("\"'")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    metadata: dict[str, Any] = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = _parse_value(value)

    return metadata, parts[2].lstrip("\n")


@dataclass
class WikiPage:
    id: str
    slug: str
    title: str
    type: str
    tags: list[str]
    source: str
    updated_at: str
    related_pages: list[str]
    body: str
    path: str
    metadata: dict[str, Any]

    def summary(self) -> dict[str, Any]:
        item = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "type": self.type,
            "tags": self.tags,
            "source": self.source,
            "updated_at": self.updated_at,
            "related_pages": self.related_pages,
        }
        for key in SUMMARY_METADATA_KEYS:
            if key in self.metadata:
                item[key] = self.metadata[key]
        return item

    def to_dict(self) -> dict[str, Any]:
        item = asdict(self)
        for key in SUMMARY_METADATA_KEYS:
            if key in self.metadata:
                item[key] = self.metadata[key]
        return item


WIKI_PAGE_FIELDS = {field.name for field in fields(WikiPage)}


def _wiki_page_from_dict(data: dict[str, Any]) -> WikiPage:
    return WikiPage(**{key: value for key, value in data.items() if key in WIKI_PAGE_FIELDS})


class WikiStore:
    def __init__(self, root: Path | str = DEFAULT_WIKI_DIR):
        self.root = Path(root).resolve()
        self._pages_cache: list[WikiPage] | None = None

    def pages(self) -> list[WikiPage]:
        if self._pages_cache is not None:
            return self._pages_cache
        pages: list[WikiPage] = []
        for path in sorted(self.root.rglob("*.md")):
            page = self._load_page(path)
            if page:
                pages.append(page)
        self._pages_cache = pages
        return pages

    def list_pages(
        self,
        type_filter: str | None = None,
        tag: str | None = None,
        province: str | None = None,
        district: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        result = []
        for page in self.pages():
            if type_filter and page.type != type_filter:
                continue
            if tag and tag not in page.tags:
                continue
            if province and page.metadata.get("province") != province:
                continue
            if district and page.metadata.get("district") != district:
                continue
            result.append(page.summary())
            if limit and len(result) >= limit:
                break
        return result

    def get_page(self, page_id: str) -> dict[str, Any]:
        for page in self.pages():
            if page.id == page_id or page.slug == page_id:
                return page.to_dict()
        raise KeyError(f"Wiki page not found: {page_id}")

    def search_pages(
        self,
        query: str,
        type_filter: str | None = None,
        tags: list[str] | None = None,
        province: str | None = None,
        district: str | None = None,
        limit: int | None = 50,
    ) -> list[dict[str, Any]]:
        query_terms = [term for term in re.split(r"\s+", query.strip().lower()) if term]
        tag_filter = set(tags or [])
        matches: list[dict[str, Any]] = []

        for page in self.pages():
            if type_filter and page.type != type_filter:
                continue
            if tag_filter and not tag_filter.issubset(set(page.tags)):
                continue
            if province and page.metadata.get("province") != province:
                continue
            if district and page.metadata.get("district") != district:
                continue

            haystack = " ".join(
                [
                    page.title,
                    page.type,
                    str(page.metadata.get("province", "")),
                    str(page.metadata.get("district", "")),
                    " ".join(page.tags),
                    " ".join(_normalize_string_list(page.metadata.get("ontology_terms", []))),
                    page.body,
                ]
            ).lower()
            score = 0
            if not query_terms:
                score = 1
            else:
                for term in query_terms:
                    if term in haystack:
                        score += max(1, haystack.count(term))

            if score:
                item = page.summary()
                item["score"] = score
                item["snippet"] = _snippet(page.body, query_terms)
                matches.append(item)

        sorted_matches = sorted(matches, key=lambda item: (-item["score"], item["title"]))
        return sorted_matches[:limit] if limit else sorted_matches

    def get_related_pages(self, page_id: str) -> list[dict[str, Any]]:
        page = _wiki_page_from_dict(self.get_page(page_id))
        all_pages = {candidate.id: candidate for candidate in self.pages()}
        related: list[dict[str, Any]] = []
        for related_id in page.related_pages:
            related_page = all_pages.get(related_id)
            if related_page:
                item = related_page.summary()
                item["relation"] = _relation_label(page.type, related_page.type)
                related.append(item)
        return related

    def create_page(
        self,
        title: str,
        page_type: str,
        body: str,
        tags: list[str] | None = None,
        related_pages: list[str] | None = None,
        source: str = "agent_written",
        page_id: str | None = None,
        confirmed: bool = False,
        overwrite: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_type = _normalize_page_type(page_type)
        normalized_tags = _normalize_string_list(tags)
        normalized_related = _normalize_string_list(related_pages)
        inferred_terms = extract_ontology_terms(" ".join([title, body, " ".join(normalized_tags)]))
        normalized_tags = _merge_unique(normalized_tags, inferred_terms)
        safe_id = _clean_page_id(page_id or f"{normalized_type}-{slugify(title)}")

        if not overwrite:
            safe_id = self._unique_page_id(normalized_type, safe_id)

        extra_metadata = dict(metadata or {})
        if inferred_terms:
            extra_metadata["ontology_terms"] = _merge_unique(
                _normalize_string_list(extra_metadata.get("ontology_terms", [])),
                inferred_terms,
            )
            normalized_related = _merge_unique(
                normalized_related,
                self._related_ontology_ids(str(extra_metadata.get("province", "")), inferred_terms),
            )
        markdown = _render_page_markdown(
            page_id=safe_id,
            title=title,
            page_type=normalized_type,
            tags=normalized_tags,
            source=source,
            related_pages=normalized_related,
            body=body,
            extra_metadata=extra_metadata,
        )
        path = self._path_for_page(normalized_type, safe_id)

        if not confirmed:
            return {
                "draft_id": safe_id,
                "draft_path": self._relative_path(path),
                "draft_markdown": markdown,
                "file_written": False,
                "needs_user_confirmation": True,
                "tools_used": ["create_page"],
            }

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        self._pages_cache = None
        return {
            "page": self.get_page(safe_id),
            "created": True,
            "file_written": True,
            "tools_used": ["create_page"],
        }

    def update_page(
        self,
        page_id: str,
        title: str | None = None,
        body: str | None = None,
        tags: list[str] | None = None,
        related_pages: list[str] | None = None,
        source: str | None = None,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        current = _wiki_page_from_dict(self.get_page(page_id))
        updated_tags = current.tags if tags is None else _normalize_string_list(tags)
        updated_related = current.related_pages if related_pages is None else _normalize_string_list(related_pages)
        inferred_terms = extract_ontology_terms(
            " ".join([title or current.title, body if body is not None else current.body, " ".join(updated_tags)])
        )
        updated_tags = _merge_unique(updated_tags, inferred_terms)
        extra_metadata = dict(current.metadata)
        if inferred_terms:
            extra_metadata["ontology_terms"] = _merge_unique(
                _normalize_string_list(extra_metadata.get("ontology_terms", [])),
                inferred_terms,
            )
            updated_related = _merge_unique(
                updated_related,
                self._related_ontology_ids(str(extra_metadata.get("province", "")), inferred_terms),
            )
        markdown = _render_page_markdown(
            page_id=current.id,
            title=title or current.title,
            page_type=current.type,
            tags=updated_tags,
            source=source or current.source,
            related_pages=updated_related,
            body=body if body is not None else current.body,
            extra_metadata=extra_metadata,
        )
        path = (self.root / current.path).resolve()
        try:
            path.relative_to(self.root.resolve())
        except ValueError as exc:
            raise ValueError(f"Refusing to update page outside wiki root: {current.path}") from exc

        if not confirmed:
            return {
                "draft_id": current.id,
                "draft_path": current.path,
                "draft_markdown": markdown,
                "file_written": False,
                "needs_user_confirmation": True,
                "tools_used": ["update_page", "get_page"],
            }

        path.write_text(markdown, encoding="utf-8")
        self._pages_cache = None
        return {
            "page": self.get_page(current.id),
            "updated": True,
            "file_written": True,
            "tools_used": ["update_page", "get_page"],
        }

    def _path_for_page(self, page_type: str, page_id: str) -> Path:
        return self.root / PAGE_TYPE_DIRS[page_type] / f"{page_id}.md"

    def _relative_path(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def _unique_page_id(self, page_type: str, page_id: str) -> str:
        candidate = page_id
        suffix = 2
        while self._path_for_page(page_type, candidate).exists():
            candidate = f"{page_id}-{suffix}"
            suffix += 1
        return candidate

    def _related_ontology_ids(self, province: str, terms: list[str], limit: int = 8) -> list[str]:
        related: list[str] = []
        for page in self.pages():
            if page.type != "ontology":
                continue
            if province and page.metadata.get("province") != province:
                continue
            ontology_terms = _normalize_string_list(page.metadata.get("ontology_terms", []))
            if any(term in ontology_terms for term in terms):
                related.append(page.id)
            if len(related) >= limit:
                break
        return related

    def _load_page(self, path: Path) -> WikiPage | None:
        text = path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
        rel_slug = path.relative_to(self.root).with_suffix("").as_posix()
        fallback_id = rel_slug.replace("/", "-")
        tags = metadata.get("tags", [])
        related_pages = metadata.get("related_pages", [])

        if isinstance(tags, str):
            tags = [tags]
        if isinstance(related_pages, str):
            related_pages = [related_pages]

        known_keys = {
            "id",
            "slug",
            "title",
            "type",
            "tags",
            "source",
            "updated_at",
            "related_pages",
        }
        extra_metadata = {key: value for key, value in metadata.items() if key not in known_keys}

        return WikiPage(
            id=str(metadata.get("id") or fallback_id),
            slug=str(metadata.get("slug") or rel_slug),
            title=str(metadata.get("title") or path.stem.replace("-", " ").title()),
            type=str(metadata.get("type") or path.parent.name.rstrip("s")),
            tags=[str(tag) for tag in tags],
            source=str(metadata.get("source") or "local"),
            updated_at=str(metadata.get("updated_at") or date.fromtimestamp(path.stat().st_mtime)),
            related_pages=[str(related_id) for related_id in related_pages],
            body=body.strip(),
            path=self._relative_path(path),
            metadata=extra_metadata,
        )


def create_field_note(raw_note: str, visited_at: str, region: str = "", property_name: str = "") -> dict[str, Any]:
    title_target = property_name or region or "field note"
    title = f"{visited_at} {title_target} 임장 노트"
    observations = _split_note(raw_note)
    tags = ["field-note"]
    if region:
        tags.append(slugify(region))
    if property_name:
        tags.append(slugify(property_name))

    body_lines = [
        f"# {title}",
        "",
        "## 관찰 내용",
        *[f"- {line}" for line in observations],
        "",
        "## 확인 필요",
        "- 가격, 관리비, 계약 조건은 원문 또는 공인 자료로 재확인",
        "- 투자 또는 계약 판단은 사용자가 최종 결정",
    ]

    return {
        "draft_title": title,
        "draft_markdown": "\n".join(body_lines),
        "tags": tags,
        "needs_user_confirmation": True,
        "tools_used": ["create_field_note"],
    }


def compare_properties(property_page_ids: list[str], store: WikiStore | None = None) -> dict[str, Any]:
    store = store or WikiStore()
    pages = [_wiki_page_from_dict(store.get_page(page_id)) for page_id in property_page_ids]
    criteria = [
        ("가격/비용", ["보증금", "월세", "매매가", "가격", "관리비"]),
        ("면적/구조", ["면적", "전용", "구조"]),
        ("교통", ["역", "버스", "도보", "교통"]),
        ("소음/채광", ["소음", "채광", "남향", "창", "환기"]),
        ("리스크", ["리스크", "확인 필요", "주의", "누수", "어두움"]),
    ]

    rows: list[dict[str, str]] = []
    for criterion, keywords in criteria:
        row = {"criterion": criterion}
        for page in pages:
            row[page.id] = _collect_lines(page.body, keywords)
        rows.append(row)

    return {
        "properties": [page.summary() for page in pages],
        "comparison": rows,
        "risk_notes": [
            "문서에서 확인되지 않은 항목은 현장 또는 계약 자료로 재확인해야 합니다.",
            "본 비교는 정보 정리이며 투자 또는 계약 추천이 아닙니다.",
        ],
        "tools_used": ["compare_properties", "get_page"],
    }


def get_knowledge_graph(store: WikiStore | None = None) -> dict[str, Any]:
    store = store or WikiStore()
    pages = store.list_pages()
    return _build_graph_response(pages, ["get_knowledge_graph", "list_pages"])


def get_scoped_graph(
    store: WikiStore | None = None,
    province: str | None = None,
    district: str | None = None,
    limit: int = 900,
) -> dict[str, Any]:
    store = store or WikiStore()
    pages = store.list_pages(province=province, district=district)
    pages = _prioritize_graph_pages(pages, limit)
    response = _build_graph_response(pages, ["get_scoped_graph", "list_pages"])
    response["scope"] = {"province": province, "district": district, "limit": limit}
    return response


def get_atlas(store: WikiStore | None = None) -> dict[str, Any]:
    store = store or WikiStore()
    atlas: dict[str, dict[str, Any]] = {}
    for page in store.list_pages():
        province = page.get("province")
        if not province:
            continue
        entry = atlas.setdefault(
            str(province),
            {
                "province": province,
                "page_count": 0,
                "property_count": 0,
                "districts": {},
                "ontology_terms": {},
            },
        )
        entry["page_count"] += 1
        if page["type"] == "property":
            entry["property_count"] += 1
        district = page.get("district")
        if district:
            entry["districts"][district] = entry["districts"].get(district, 0) + 1
        for term in _normalize_string_list(page.get("ontology_terms", [])):
            entry["ontology_terms"][term] = entry["ontology_terms"].get(term, 0) + 1

    provinces = []
    for entry in atlas.values():
        entry["districts"] = [
            {"name": name, "page_count": count}
            for name, count in sorted(entry["districts"].items(), key=lambda item: (-item[1], item[0]))[:12]
        ]
        entry["ontology_terms"] = [
            {"term": term, "count": count}
            for term, count in sorted(entry["ontology_terms"].items(), key=lambda item: (-item[1], item[0]))[:8]
        ]
        provinces.append(entry)

    return {
        "provinces": sorted(provinces, key=lambda item: item["province"]),
        "tools_used": ["get_atlas", "list_pages"],
    }


def recommend_properties(
    query: str,
    store: WikiStore | None = None,
    province: str | None = None,
    district: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    store = store or WikiStore()
    inferred_province = province or infer_province(query)
    inferred_terms = extract_ontology_terms(query)
    query_terms = [term for term in re.split(r"\s+", query.strip().lower()) if term]
    candidates = [
        page
        for page in store.pages()
        if page.type == "property"
        and (not inferred_province or page.metadata.get("province") == inferred_province)
        and (not district or page.metadata.get("district") == district)
    ]
    scored: list[dict[str, Any]] = []

    for page in candidates:
        ontology_terms = _normalize_string_list(page.metadata.get("ontology_terms", []))
        features = _normalize_string_list(page.metadata.get("features", []))
        scores = page.metadata.get("scores", {})
        if not isinstance(scores, dict):
            scores = {}

        score = 0.0
        reasons: list[str] = []
        matched_terms = [term for term in inferred_terms if term in ontology_terms or term in features]
        score += len(matched_terms) * 18
        for term in matched_terms:
            label = _ontology_label(term)
            reasons.append(f"{label} 조건과 연결됨")

        if inferred_province and page.metadata.get("province") == inferred_province:
            score += 15
            reasons.append(f"{inferred_province} 지역 일치")
        if district and page.metadata.get("district") == district:
            score += 10
            reasons.append(f"{district} 세부 지역 일치")

        for term in inferred_terms:
            value = scores.get(term)
            if isinstance(value, (int, float)):
                score += float(value)
        if "low_noise" in inferred_terms and "대로변 소음" in page.body:
            score -= 10

        haystack = " ".join([page.title, page.body, " ".join(page.tags), " ".join(features)]).lower()
        for term in query_terms:
            if term in haystack:
                score += 1

        if score > 0:
            scored.append(
                {
                    "page": page.summary(),
                    "score": round(score, 2),
                    "matched_terms": matched_terms,
                    "ontology_path": _ontology_path(inferred_province, matched_terms, page),
                    "reasons": reasons[:5] or ["질문 키워드와 Page 본문이 연결됨"],
                    "snippet": _snippet(page.body, query_terms),
                }
            )

    scored.sort(key=lambda item: (-item["score"], item["page"]["title"]))
    return {
        "query": query,
        "normalized": {
            "province": inferred_province,
            "district": district,
            "ontology_terms": inferred_terms,
        },
        "recommendations": scored[:limit],
        "tools_used": ["recommend_properties", "extract_ontology_terms", "list_pages", "get_page"],
    }


def extract_ontology_terms(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for term, aliases in ONTOLOGY_ALIASES.items():
        if term in lowered or any(alias.lower() in lowered for alias in aliases):
            found.append(term)
    return found


def infer_province(text: str) -> str | None:
    for alias, province in REGION_ALIASES.items():
        if alias in text:
            return province
    return None


def _build_graph_response(pages: list[dict[str, Any]], tools_used: list[str]) -> dict[str, Any]:
    page_ids = {page["id"] for page in pages}
    edge_map: dict[tuple[str, str], dict[str, Any]] = {}

    for page in pages:
        for related_id in page.get("related_pages", []):
            if related_id not in page_ids or related_id == page["id"]:
                continue

            source, target = sorted([page["id"], related_id])
            edge = edge_map.setdefault(
                (source, target),
                {
                    "source": source,
                    "target": target,
                    "weight": 0,
                    "directions": [],
                },
            )
            edge["weight"] += 1
            edge["directions"].append({"from": page["id"], "to": related_id})

    return {
        "nodes": pages,
        "edges": list(edge_map.values()),
        "tools_used": tools_used,
    }


def _prioritize_graph_pages(pages: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(pages) <= limit:
        return pages
    type_rank = {"region": 0, "ontology": 1, "property": 2, "field_note": 3, "checklist": 4, "trade_summary": 5}
    return sorted(pages, key=lambda item: (type_rank.get(item["type"], 9), item["title"]))[:limit]


def _normalize_page_type(page_type: str) -> str:
    normalized = page_type.strip()
    if normalized not in PAGE_TYPE_DIRS:
        allowed = ", ".join(sorted(PAGE_TYPE_DIRS))
        raise ValueError(f"Unsupported page type: {page_type}. Allowed types: {allowed}")
    return normalized


def _normalize_string_list(values: list[str] | str | None) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    result: list[str] = []
    for value in values:
        item = str(value).strip()
        if item and item not in result:
            result.append(item)
    return result


def _merge_unique(first: list[str], second: list[str]) -> list[str]:
    result = list(first)
    for item in second:
        if item not in result:
            result.append(item)
    return result


def _clean_page_id(value: str) -> str:
    page_id = slugify(value)
    if not re.match(r"^[0-9A-Za-z가-힣][0-9A-Za-z가-힣-]*$", page_id):
        raise ValueError(f"Invalid page id: {value}")
    return page_id


def _format_frontmatter_list(values: list[str]) -> str:
    return "[" + ", ".join(json.dumps(value, ensure_ascii=False) for value in values) + "]"


def _render_page_markdown(
    page_id: str,
    title: str,
    page_type: str,
    tags: list[str],
    source: str,
    related_pages: list[str],
    body: str,
    extra_metadata: dict[str, Any] | None = None,
) -> str:
    clean_body = body.strip()
    if not clean_body.startswith("#"):
        clean_body = f"# {title}\n\n{clean_body}"
    extra_lines = ""
    for key, value in (extra_metadata or {}).items():
        if key in {"id", "title", "type", "tags", "source", "updated_at", "related_pages"}:
            continue
        extra_lines += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
    return (
        "---\n"
        f"id: {page_id}\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"type: {page_type}\n"
        f"tags: {_format_frontmatter_list(tags)}\n"
        f"source: {json.dumps(source, ensure_ascii=False)}\n"
        f"updated_at: {date.today().isoformat()}\n"
        f"related_pages: {_format_frontmatter_list(related_pages)}\n"
        f"{extra_lines}"
        "---\n\n"
        f"{clean_body}\n"
    )


def _ontology_label(term: str) -> str:
    labels = {
        "low_noise": "저소음",
        "station_access": "역 접근성",
        "sunlight": "채광",
        "safety": "야간 안전",
        "green_access": "녹지 접근성",
        "river_access": "수변 접근성",
        "school_district": "교육 인프라",
        "office_access": "직주근접",
        "low_rent": "비용 접근성",
        "new_building": "신축/준신축",
        "pet_friendly": "반려동물",
        "parking": "주차",
    }
    return labels.get(term, term)


def _ontology_path(province: str | None, terms: list[str], page: WikiPage) -> list[dict[str, str]]:
    path: list[dict[str, str]] = []
    if province:
        path.append({"type": "province", "label": province})
    district = page.metadata.get("district")
    if district:
        path.append({"type": "district", "label": str(district)})
    for term in terms:
        path.append({"type": "ontology", "label": _ontology_label(term), "term": term})
    path.append({"type": "property", "label": page.title, "page_id": page.id})
    return path


def fetch_apt_trade(lawd_cd: str, deal_ymd: str) -> dict[str, Any]:
    endpoint = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    return _fetch_public_data(endpoint, lawd_cd, deal_ymd, "fetch_apt_trade", _sample_trade)


def fetch_apt_rent(lawd_cd: str, deal_ymd: str) -> dict[str, Any]:
    endpoint = "https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
    return _fetch_public_data(endpoint, lawd_cd, deal_ymd, "fetch_apt_rent", _sample_rent)


def _fetch_public_data(endpoint: str, lawd_cd: str, deal_ymd: str, tool_name: str, fallback_factory) -> dict[str, Any]:
    _load_local_env()
    service_key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not service_key:
        return fallback_factory(lawd_cd, deal_ymd, "DATA_GO_KR_SERVICE_KEY is not configured")

    params = urllib.parse.urlencode(
        {
            "serviceKey": service_key,
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": deal_ymd,
            "numOfRows": "20",
        }
    )
    url = f"{endpoint}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=12) as response:
            payload = response.read()
        root = ET.fromstring(payload)
        items = []
        for item in root.findall(".//item"):
            record = {child.tag: (child.text or "").strip() for child in item}
            items.append(record)
        return {
            "source": "public_api",
            "query": {"LAWD_CD": lawd_cd, "DEAL_YMD": deal_ymd},
            "items": items,
            "tools_used": [tool_name],
        }
    except Exception as exc:  # Public data portals often return HTML/XML error payloads.
        return fallback_factory(lawd_cd, deal_ymd, f"public API request failed: {exc.__class__.__name__}")


def _load_local_env() -> None:
    for env_path in [ROOT / ".env", Path.cwd() / ".env"]:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _sample_trade(lawd_cd: str, deal_ymd: str, reason: str) -> dict[str, Any]:
    return {
        "source": "sample_data",
        "fallback_reason": reason,
        "query": {"LAWD_CD": lawd_cd, "DEAL_YMD": deal_ymd},
        "items": [
            {
                "apt_name": "Sample Heights",
                "dong": "Jamsil-dong",
                "exclusive_area": "84.9",
                "deal_amount": "185000",
                "deal_day": "15",
                "floor": "12",
                "build_year": "2014",
            }
        ],
        "tools_used": ["fetch_apt_trade"],
    }


def _sample_rent(lawd_cd: str, deal_ymd: str, reason: str) -> dict[str, Any]:
    return {
        "source": "sample_data",
        "fallback_reason": reason,
        "query": {"LAWD_CD": lawd_cd, "DEAL_YMD": deal_ymd},
        "items": [
            {
                "apt_name": "Sample Heights",
                "dong": "Jamsil-dong",
                "exclusive_area": "84.9",
                "deposit": "50000",
                "monthly_rent": "0",
                "deal_day": "15",
                "floor": "9",
                "contract_term": "2024.06-2026.06",
            }
        ],
        "tools_used": ["fetch_apt_rent"],
    }


def _snippet(body: str, terms: list[str]) -> str:
    lines = [line.strip("#- ") for line in body.splitlines() if line.strip()]
    if not terms:
        return lines[0] if lines else ""
    for line in lines:
        lowered = line.lower()
        if any(term in lowered for term in terms):
            return line[:180]
    return lines[0][:180] if lines else ""


def _relation_label(source_type: str, related_type: str) -> str:
    labels = {
        ("property", "region"): "located_in",
        ("property", "checklist"): "checked_by",
        ("property", "field_note"): "observed_in",
        ("property", "trade_summary"): "priced_by",
        ("field_note", "property"): "describes",
        ("trade_summary", "property"): "supports",
    }
    return labels.get((source_type, related_type), "related")


def _split_note(raw_note: str) -> list[str]:
    chunks = re.split(r"[\n.;!?]+", raw_note)
    return [chunk.strip(" -") for chunk in chunks if chunk.strip(" -")]


def _collect_lines(body: str, keywords: list[str]) -> str:
    matches = []
    for line in body.splitlines():
        clean = line.strip(" #-")
        if clean in {"기본 정보", "현장 관찰", "리스크", "확인 필요"}:
            continue
        if clean and any(keyword in clean for keyword in keywords):
            matches.append(clean)
    if not matches:
        return "문서에서 확인되지 않음"
    return " / ".join(matches[:3])
