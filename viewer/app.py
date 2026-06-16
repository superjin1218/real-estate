from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.wiki_store import WikiStore, compare_properties, fetch_apt_rent, fetch_apt_trade  # noqa: E402


app = FastAPI(title="Real Estate Field Wiki")
store = WikiStore(ROOT / "wiki")
static_dir = ROOT / "viewer" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.head("/")
def index_head() -> Response:
    return Response(status_code=200)


@app.get("/api/pages")
def api_list_pages(type: str | None = None, tag: str | None = None):
    return {"pages": store.list_pages(type_filter=type, tag=tag), "tools_used": ["list_pages"]}


@app.get("/api/pages/{page_id}")
def api_get_page(page_id: str):
    try:
        return {"page": store.get_page(page_id), "tools_used": ["get_page"]}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
):
    return {
        "pages": store.search_pages(query=q, type_filter=type, tags=tags),
        "tools_used": ["search_pages"],
    }


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
