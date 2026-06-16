from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WIKI_DIR = ROOT / "wiki"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "untitled"


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
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

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "type": self.type,
            "tags": self.tags,
            "source": self.source,
            "updated_at": self.updated_at,
            "related_pages": self.related_pages,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class WikiStore:
    def __init__(self, root: Path | str = DEFAULT_WIKI_DIR):
        self.root = Path(root)

    def pages(self) -> list[WikiPage]:
        pages: list[WikiPage] = []
        for path in sorted(self.root.rglob("*.md")):
            page = self._load_page(path)
            if page:
                pages.append(page)
        return pages

    def list_pages(self, type_filter: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
        result = []
        for page in self.pages():
            if type_filter and page.type != type_filter:
                continue
            if tag and tag not in page.tags:
                continue
            result.append(page.summary())
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
    ) -> list[dict[str, Any]]:
        query_terms = [term for term in re.split(r"\s+", query.strip().lower()) if term]
        tag_filter = set(tags or [])
        matches: list[dict[str, Any]] = []

        for page in self.pages():
            if type_filter and page.type != type_filter:
                continue
            if tag_filter and not tag_filter.issubset(set(page.tags)):
                continue

            haystack = " ".join([page.title, page.type, " ".join(page.tags), page.body]).lower()
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

        return sorted(matches, key=lambda item: (-item["score"], item["title"]))

    def get_related_pages(self, page_id: str) -> list[dict[str, Any]]:
        page = WikiPage(**self.get_page(page_id))
        all_pages = {candidate.id: candidate for candidate in self.pages()}
        related: list[dict[str, Any]] = []
        for related_id in page.related_pages:
            related_page = all_pages.get(related_id)
            if related_page:
                item = related_page.summary()
                item["relation"] = _relation_label(page.type, related_page.type)
                related.append(item)
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
            path=path.relative_to(ROOT).as_posix(),
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
    pages = [WikiPage(**store.get_page(page_id)) for page_id in property_page_ids]
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
