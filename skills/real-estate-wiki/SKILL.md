---
name: real-estate-wiki
description: Use the Real Estate Field Wiki MCP tools to search nationwide field-note pages, inspect regional atlas graphs, normalize natural-language housing conditions into ontology terms, recommend candidate properties, draft or write approved wiki pages, compare properties, and fetch apartment trade or rent sample data.
---

# Real Estate Wiki Skill

Use this skill when the user asks about Korean real-estate field notes, regional housing characteristics, candidate properties, ontology-linked search, map/graph exploration, lease risk checks, or apartment transaction data stored in this repository.

## Workflow

1. Start with `recommend_properties` when the user asks for a house matching natural-language conditions such as "소음이 없는 서울 집".
2. Use `extract_ontology_terms` when you need to show which terms were inferred from a query or new page body.
3. Use `get_atlas` for nationwide province summaries and map entry points.
4. Use `get_scoped_graph` for Obsidian-style regional graph exploration. Prefer province/district scopes over `get_knowledge_graph` because the generated wiki contains 10,000 pages.
5. Call `list_pages` or `search_pages` to find relevant Wiki pages. Include `province`, `district`, `type`, `tag`, or `limit` filters when possible.
6. Call `get_page` for every page used as evidence.
7. Call `get_related_pages` when a property, region, checklist, ontology page, or trade summary may be connected.
8. Call `create_field_note` for raw note drafting. Treat the result as a draft requiring user confirmation.
9. Call `create_page` or `update_page` with `confirmed=false` for write drafts, and only use `confirmed=true` after explicit user approval. Saved pages automatically receive ontology terms and related ontology links.
10. Call `compare_properties` only from the comparison workflow. Do not recommend a final decision.
11. Call `fetch_apt_trade` or `fetch_apt_rent` for transaction records. If `source` is `sample_data`, say that clearly.

## Safety

- No contract recommendation.
- No legal, tax, loan, or investment judgment.
- No invented facts outside tool results.
- No page writes without user approval.
- No page deletion.
- No full 10,000-page graph rendering unless the user explicitly asks for it.
- No API keys in prompts, pages, logs, or screenshots.
