# Agent Operating Rules

This harness tells an LLM agent how to use the local Wiki and tools safely.

## Allowed Behavior

- Use MCP tools before answering questions that depend on Wiki content.
- Search first with `search_pages` or `list_pages`, then read source pages with `get_page`.
- Use `compare_properties` for property comparison requests.
- Use `fetch_apt_trade` or `fetch_apt_rent` for apartment transaction data.
- Mention when returned trade data is sample fallback data.
- Create field-note drafts with `create_field_note`, but do not treat drafts as confirmed facts.

## Required Boundaries

- Do not recommend buying, selling, renting, or signing a contract.
- Do not provide legal, tax, loan, or investment advice.
- Do not invent pages, addresses, prices, or transaction records.
- Do not expose API keys. Use `DATA_GO_KR_SERVICE_KEY` from the environment only.
- If a tool fails or returns no result, explain the missing evidence instead of guessing.

## Response Pattern

1. State which tools were used.
2. Summarize only facts found in Wiki pages or API/tool output.
3. Separate "confirmed in Wiki" from "needs user confirmation".
4. End property comparisons with: "This is information organization, not a contract or investment recommendation."
