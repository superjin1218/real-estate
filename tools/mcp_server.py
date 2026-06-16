from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from wiki_store import (
    WikiStore,
    compare_properties as compare_property_pages,
    create_field_note as build_field_note,
    extract_ontology_terms as extract_terms,
    fetch_apt_rent as fetch_rent_data,
    fetch_apt_trade as fetch_trade_data,
    get_atlas as build_atlas,
    get_knowledge_graph as build_knowledge_graph,
    get_scoped_graph as build_scoped_graph,
    recommend_properties as recommend_property_pages,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # The self-test path works without the optional MCP SDK.
    FastMCP = None


ROOT = Path(__file__).resolve().parents[1]
STORE = WikiStore(ROOT / "wiki")
MCP_NAME = "real-estate-field-wiki"

if FastMCP:
    mcp = FastMCP(MCP_NAME)
else:
    mcp = None


def list_pages(type: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
    return STORE.list_pages(type_filter=type, tag=tag)


def get_page(page_id: str) -> dict[str, Any]:
    return STORE.get_page(page_id)


def search_pages(
    query: str,
    type: str | None = None,
    tags: list[str] | None = None,
    province: str | None = None,
    district: str | None = None,
    limit: int | None = 50,
) -> list[dict[str, Any]]:
    return STORE.search_pages(query=query, type_filter=type, tags=tags, province=province, district=district, limit=limit)


def get_related_pages(page_id: str) -> list[dict[str, Any]]:
    return STORE.get_related_pages(page_id)


def get_knowledge_graph() -> dict[str, Any]:
    return build_knowledge_graph(STORE)


def get_atlas() -> dict[str, Any]:
    return build_atlas(STORE)


def get_scoped_graph(province: str | None = None, district: str | None = None, limit: int = 900) -> dict[str, Any]:
    return build_scoped_graph(STORE, province=province, district=district, limit=limit)


def extract_ontology_terms(text: str) -> list[str]:
    return extract_terms(text)


def recommend_properties(
    query: str,
    province: str | None = None,
    district: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    return recommend_property_pages(query=query, store=STORE, province=province, district=district, limit=limit)


def create_field_note(raw_note: str, visited_at: str, region: str = "", property: str = "") -> dict[str, Any]:
    return build_field_note(raw_note, visited_at=visited_at, region=region, property_name=property)


def create_page(
    title: str,
    type: str,
    body: str,
    tags: list[str] | None = None,
    related_pages: list[str] | None = None,
    source: str = "agent_written",
    page_id: str | None = None,
    confirmed: bool = False,
    overwrite: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return STORE.create_page(
        title=title,
        page_type=type,
        body=body,
        tags=tags,
        related_pages=related_pages,
        source=source,
        page_id=page_id,
        confirmed=confirmed,
        overwrite=overwrite,
        metadata=metadata,
    )


def update_page(
    page_id: str,
    title: str | None = None,
    body: str | None = None,
    tags: list[str] | None = None,
    related_pages: list[str] | None = None,
    source: str | None = None,
    confirmed: bool = False,
) -> dict[str, Any]:
    return STORE.update_page(
        page_id=page_id,
        title=title,
        body=body,
        tags=tags,
        related_pages=related_pages,
        source=source,
        confirmed=confirmed,
    )


def compare_properties(property_page_ids: list[str]) -> dict[str, Any]:
    return compare_property_pages(property_page_ids, STORE)


def fetch_apt_trade(lawd_cd: str, deal_ymd: str) -> dict[str, Any]:
    return fetch_trade_data(lawd_cd=lawd_cd, deal_ymd=deal_ymd)


def fetch_apt_rent(lawd_cd: str, deal_ymd: str) -> dict[str, Any]:
    return fetch_rent_data(lawd_cd=lawd_cd, deal_ymd=deal_ymd)


if mcp:
    mcp.tool()(list_pages)
    mcp.tool()(get_page)
    mcp.tool()(search_pages)
    mcp.tool()(get_related_pages)
    mcp.tool()(get_knowledge_graph)
    mcp.tool()(get_atlas)
    mcp.tool()(get_scoped_graph)
    mcp.tool()(extract_ontology_terms)
    mcp.tool()(recommend_properties)
    mcp.tool()(create_field_note)
    mcp.tool()(create_page)
    mcp.tool()(update_page)
    mcp.tool()(compare_properties)
    mcp.tool()(fetch_apt_trade)
    mcp.tool()(fetch_apt_rent)


def self_test() -> dict[str, Any]:
    property_ids = [page["id"] for page in list_pages(type="property")][:2]
    return {
        "tools": [
            "list_pages",
            "get_page",
            "search_pages",
            "get_related_pages",
            "get_knowledge_graph",
            "get_atlas",
            "get_scoped_graph",
            "extract_ontology_terms",
            "recommend_properties",
            "create_field_note",
            "create_page",
            "update_page",
            "compare_properties",
            "fetch_apt_trade",
            "fetch_apt_rent",
        ],
        "page_count": len(list_pages()),
        "graph_sample": {
            "node_count": len(get_scoped_graph(province="서울특별시")["nodes"]),
            "edge_count": len(get_scoped_graph(province="서울특별시")["edges"]),
        },
        "search_sample": search_pages("잠실 소음", limit=5),
        "atlas_sample": get_atlas()["provinces"][:3],
        "recommend_sample": recommend_properties("소음이 없는 서울에 있는 집 찾아줘", limit=3),
        "comparison_sample": compare_properties(property_ids) if len(property_ids) >= 2 else None,
        "rent_sample": fetch_apt_rent("11710", "202405"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP server for Real Estate Field Wiki.")
    parser.add_argument("--self-test", action="store_true", help="Run local tool checks without starting MCP stdio.")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False, indent=2))
        return 0

    if not mcp:
        raise SystemExit("Install dependencies first: pip install -r requirements.txt")

    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
