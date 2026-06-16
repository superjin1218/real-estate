from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.wiki_store import (  # noqa: E402
    WikiStore,
    compare_properties,
    fetch_apt_rent,
    fetch_apt_trade,
    get_atlas,
    get_knowledge_graph,
    get_scoped_graph,
    recommend_properties,
)


app = FastAPI(title="Real Estate Field Wiki")
store = WikiStore(ROOT / "wiki")
static_dir = ROOT / "viewer" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class PageWriteRequest(BaseModel):
    title: str
    type: str = "field_note"
    body: str
    tags: list[str] = Field(default_factory=list)
    related_pages: list[str] = Field(default_factory=list)
    source: str = "gui_writer"
    page_id: str | None = None
    overwrite: bool = False
    province: str | None = None
    district: str | None = None


class PageUpdateRequest(BaseModel):
    title: str | None = None
    body: str | None = None
    tags: list[str] | None = None
    related_pages: list[str] | None = None
    source: str | None = None


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.head("/")
def index_head() -> Response:
    return Response(status_code=200)


@app.get("/api/pages")
def api_list_pages(
    type: str | None = None,
    tag: str | None = None,
    province: str | None = None,
    district: str | None = None,
    limit: int | None = None,
):
    return {
        "pages": store.list_pages(type_filter=type, tag=tag, province=province, district=district, limit=limit),
        "tools_used": ["list_pages"],
    }


@app.get("/api/pages/{page_id}")
def api_get_page(page_id: str):
    try:
        return {"page": store.get_page(page_id), "tools_used": ["get_page"]}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/pages")
def api_create_page(payload: PageWriteRequest):
    try:
        return store.create_page(
            title=payload.title,
            page_type=payload.type,
            body=payload.body,
            tags=payload.tags,
            related_pages=payload.related_pages,
            source=payload.source,
            page_id=payload.page_id,
            confirmed=True,
            overwrite=payload.overwrite,
            metadata={
                key: value
                for key, value in {
                    "province": payload.province,
                    "district": payload.district,
                }.items()
                if value
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/pages/{page_id}")
def api_update_page(page_id: str, payload: PageUpdateRequest):
    try:
        return store.update_page(
            page_id=page_id,
            title=payload.title,
            body=payload.body,
            tags=payload.tags,
            related_pages=payload.related_pages,
            source=payload.source,
            confirmed=True,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/pages/{page_id}/related")
def api_get_related_pages(page_id: str):
    try:
        return {"pages": store.get_related_pages(page_id), "tools_used": ["get_related_pages"]}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/search")
def api_search_pages(
    q: str = "",
    type: str | None = None,
    tags: list[str] = Query(default=[]),
    province: str | None = None,
    district: str | None = None,
    limit: int = 50,
):
    return {
        "pages": store.search_pages(
            query=q,
            type_filter=type,
            tags=tags,
            province=province,
            district=district,
            limit=limit,
        ),
        "tools_used": ["search_pages"],
    }


@app.get("/api/graph")
def api_get_knowledge_graph(province: str | None = None, district: str | None = None, limit: int = 900):
    if province or district:
        return get_scoped_graph(store, province=province, district=district, limit=limit)
    return get_knowledge_graph(store)


@app.get("/api/atlas")
def api_get_atlas():
    return get_atlas(store)


@app.get("/api/recommend")
def api_recommend_properties(
    q: str,
    province: str | None = None,
    district: str | None = None,
    limit: int = 5,
):
    return recommend_properties(q, store=store, province=province, district=district, limit=limit)


@app.get("/api/compare")
def api_compare_properties(ids: str):
    property_page_ids = [item.strip() for item in ids.split(",") if item.strip()]
    if len(property_page_ids) < 2:
        raise HTTPException(status_code=400, detail="At least two property page IDs are required.")
    try:
        return compare_properties(property_page_ids, store)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/trade/rent")
def api_fetch_apt_rent(lawd_cd: str = "11710", deal_ymd: str = "202405"):
    return fetch_apt_rent(lawd_cd=lawd_cd, deal_ymd=deal_ymd)


@app.get("/api/trade/sale")
def api_fetch_apt_trade(lawd_cd: str = "11710", deal_ymd: str = "202405"):
    return fetch_apt_trade(lawd_cd=lawd_cd, deal_ymd=deal_ymd)
