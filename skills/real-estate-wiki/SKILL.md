---
name: real-estate-wiki
description: Use the Real Estate Field Wiki MCP tools to search pages, read source notes, compare properties, draft field notes, and fetch apartment trade or rent sample data.
---

# Real Estate Wiki Skill

Use this skill when the user asks about local field notes, candidate properties, lease risk checks, or apartment transaction data stored in this repository.

## Workflow

1. Call `list_pages` or `search_pages` to find relevant Wiki pages.
2. Call `get_page` for every page used as evidence.
3. Call `get_related_pages` when a property, region, checklist, or trade summary may be connected.
4. Call `compare_properties` only for information comparison. Do not recommend a final decision.
5. Call `create_field_note` for raw note drafting. Treat the result as a draft requiring user confirmation.
6. Call `fetch_apt_trade` or `fetch_apt_rent` for transaction records. If `source` is `sample_data`, say that clearly.

## Safety

- No contract recommendation.
- No legal, tax, loan, or investment judgment.
- No invented facts outside tool results.
- No API keys in prompts, pages, logs, or screenshots.
