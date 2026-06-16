from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from wiki_store import ROOT, create_field_note, slugify


def build_page(raw_path: Path, visited_at: str, region: str, property_name: str) -> tuple[Path, str]:
    raw_note = raw_path.read_text(encoding="utf-8")
    draft = create_field_note(raw_note, visited_at, region=region, property_name=property_name)
    title = draft["draft_title"]
    page_id = f"field-note-{slugify(title)}"
    tags = ", ".join(draft["tags"])
    body = draft["draft_markdown"]
    markdown = (
        "---\n"
        f"id: {page_id}\n"
        f"title: {title}\n"
        "type: field_note\n"
        f"tags: [{tags}]\n"
        "source: user_raw_note\n"
        f"updated_at: {date.today().isoformat()}\n"
        "related_pages: []\n"
        "---\n\n"
        f"{body}\n"
    )
    return ROOT / "wiki" / "notes" / f"{page_id}.md", markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert one raw note into a Wiki draft page.")
    parser.add_argument("raw_file", help="Path to a .md or .txt note under raw/")
    parser.add_argument("--visited-at", default=date.today().isoformat())
    parser.add_argument("--region", default="")
    parser.add_argument("--property", dest="property_name", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    output_path, markdown = build_page(Path(args.raw_file), args.visited_at, args.region, args.property_name)
    if args.dry_run:
        print(markdown)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(output_path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
