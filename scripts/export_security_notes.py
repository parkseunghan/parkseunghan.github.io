import json
import re
import sqlite3
from pathlib import Path


DB_PATH = Path(r"C:\Users\01seu\AppData\Roaming\Notion\notion.db")
REPO_ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
OUT_DIR = REPO_ROOT / "tmp" / "security-academy-source"

PAGES = [
    {
        "page_id": "312b8597-ec48-80a7-ad8f-e8476c2d5a89",
        "slug": "git-docker",
        "title": "Git&Docker",
    },
    {
        "page_id": "314b8597-ec48-8012-941b-ed00ddf332f9",
        "slug": "linux-advanced",
        "title": "리눅스 심화",
    },
    {
        "page_id": "31ab8597-ec48-804b-80ea-eaad88eb7899",
        "slug": "python",
        "title": "파이썬",
    },
    {
        "page_id": "31fb8597-ec48-805c-8d10-eef169c59077",
        "slug": "database-1",
        "title": "데이터베이스1",
    },
    {
        "page_id": "320b8597-ec48-803b-9e2b-c179dbbf9811",
        "slug": "database-2",
        "title": "데이터베이스2",
    },
    {
        "page_id": "321b8597-ec48-8084-83e2-ccd66d0fdaf6",
        "slug": "system-security-and-vulnerability-analysis",
        "title": "시스템보안 및 취약점분석",
    },
    {
        "page_id": "325b8597-ec48-8062-927f-d312914f25da",
        "slug": "system-security-2",
        "title": "시스템보안 2",
    },
    {
        "page_id": "327b8597-ec48-803f-b619-f483b74ad48a",
        "slug": "network-security",
        "title": "네트워크보안",
    },
]

MARKER_RE = re.compile(r"\[이미지:(.+?)\]")
SPACE_ID = "29af0f24-72d3-477f-a439-cccb346de9ee"


def parse_json(value):
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def load_blocks():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, type, properties, content, parent_id, format, file_ids "
        "FROM block WHERE alive=1 AND space_id=?",
        (SPACE_ID,),
    ).fetchall()
    conn.close()
    blocks = {}
    for row in rows:
        blocks[row[0]] = {
            "id": row[0],
            "type": row[1],
            "properties": parse_json(row[2]),
            "content": parse_json(row[3]) or [],
            "parent_id": row[4],
            "format": parse_json(row[5]),
            "file_ids": parse_json(row[6]) or [],
        }
    return blocks


def rich_text_to_md(spans):
    if not spans:
        return ""
    parts = []
    for span in spans:
        if not span:
            continue
        text = span[0] if isinstance(span, list) else str(span)
        marks = span[1] if isinstance(span, list) and len(span) > 1 else []
        href = None
        left = ""
        right = ""
        for mark in marks:
            if not mark:
                continue
            kind = mark[0]
            if kind == "c":
                left += "`"
                right = "`" + right
            elif kind == "b":
                left += "**"
                right = "**" + right
            elif kind == "i":
                left += "*"
                right = "*" + right
            elif kind == "s":
                left += "~~"
                right = "~~" + right
            elif kind == "a" and len(mark) > 1:
                href = mark[1]
        text = f"{left}{text}{right}"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts).strip()


def block_text(block, key="title"):
    props = block.get("properties") or {}
    return rich_text_to_md(props.get(key) or [])


def render_table(blocks, table_block):
    rows = []
    for row_id in table_block.get("content", []):
        props = blocks.get(row_id, {}).get("properties") or {}
        cells = props.get("title") or []
        row = []
        for cell in cells:
            if isinstance(cell, list) and cell and isinstance(cell[0], list):
                row.append(rich_text_to_md(cell))
            else:
                row.append(rich_text_to_md(cell if isinstance(cell, list) else [cell]))
        rows.append(row)
    if not rows:
        return []
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = [
        "| " + " | ".join(rows[0]) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines + [""]


def render_children(blocks, child_ids, image_entries, heading_base=2):
    lines = []
    pending_marker = None
    pending_image_idx = None

    for child_id in child_ids:
        block = blocks.get(child_id)
        if not block:
            continue

        btype = block["type"]
        text = block_text(block)
        marker_match = MARKER_RE.fullmatch(text) if text else None

        if marker_match:
            marker = marker_match.group(1).strip()
            if pending_image_idx is not None:
                image_entries[pending_image_idx]["marker"] = marker
                caption = image_entries[pending_image_idx]["caption"] or "설명 없음"
                lines.append(f"> [이미지 대기] `{marker}` - {caption}")
                pending_image_idx = None
                pending_marker = None
            else:
                pending_marker = marker
            continue

        if pending_image_idx is not None:
            entry = image_entries[pending_image_idx]
            label = entry["marker"] or "미지정"
            caption = entry["caption"] or "설명 없음"
            lines.append(f"> [이미지 대기] `{label}` - {caption}")
            pending_image_idx = None

        if btype == "text":
            if text:
                lines.append(text)
                lines.append("")
            if block.get("content"):
                lines.extend(render_children(blocks, block["content"], image_entries, heading_base))
            continue

        if btype in {"header", "sub_header", "sub_sub_header", "toggle", "page"}:
            if btype == "page" and heading_base == 2:
                level = 2
            else:
                level = {"header": 2, "sub_header": 3, "sub_sub_header": 4, "toggle": 3, "page": 3}.get(btype, 3)
            title = text or "제목 없음"
            lines.append(f'{"#" * level} {title}')
            lines.append("")
            if block.get("content"):
                lines.extend(render_children(blocks, block["content"], image_entries, min(level + 1, 6)))
            continue

        if btype == "bulleted_list":
            if text:
                lines.append(f"- {text}")
            if block.get("content"):
                nested = render_children(blocks, block["content"], image_entries, heading_base)
                for child_line in nested:
                    lines.append(f"  {child_line}" if child_line else "")
            continue

        if btype == "numbered_list":
            if text:
                lines.append(f"1. {text}")
            if block.get("content"):
                nested = render_children(blocks, block["content"], image_entries, heading_base)
                for child_line in nested:
                    lines.append(f"   {child_line}" if child_line else "")
            continue

        if btype == "to_do":
            mark = "x" if (block.get("properties") or {}).get("checked") else " "
            if text:
                lines.append(f"- [{mark}] {text}")
                lines.append("")
            continue

        if btype == "code":
            props = block.get("properties") or {}
            lang = rich_text_to_md(props.get("language") or []).lower()
            lines.append(f"```{lang}".rstrip())
            lines.append(text)
            lines.append("```")
            lines.append("")
            continue

        if btype in {"table", "collection_view"}:
            lines.extend(render_table(blocks, block))
            continue

        if btype == "divider":
            lines.append("---")
            lines.append("")
            continue

        if btype == "callout":
            title = text
            if title:
                lines.append(f"> {title}")
            if block.get("content"):
                nested = render_children(blocks, block["content"], image_entries, heading_base)
                for child_line in nested:
                    lines.append(f"> {child_line}" if child_line else ">")
            lines.append("")
            continue

        if btype == "quote":
            if text:
                lines.append(f"> {text}")
                lines.append("")
            continue

        if btype == "image":
            props = block.get("properties") or {}
            fmt = block.get("format") or {}
            source_url = fmt.get("display_source") or ""
            source_prop = props.get("source") or []
            if (not source_url or source_url.startswith("attachment:")) and source_prop:
                source_url = rich_text_to_md(source_prop)
            entry = {
                "block_id": block["id"],
                "marker": pending_marker,
                "caption": text,
                "file_ids": block.get("file_ids", []),
                "source_url": source_url,
            }
            image_entries.append(entry)
            pending_image_idx = len(image_entries) - 1
            pending_marker = None
            continue

    if pending_image_idx is not None:
        entry = image_entries[pending_image_idx]
        label = entry["marker"] or "미지정"
        caption = entry["caption"] or "설명 없음"
        lines.append(f"> [이미지 대기] `{label}` - {caption}")

    while lines and lines[-1] == "":
        lines.pop()
    return lines


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blocks = load_blocks()

    for page in PAGES:
        block = blocks.get(page["page_id"])
        if not block:
            continue
        image_entries = []
        body = render_children(blocks, block.get("content", []), image_entries)
        out_path = OUT_DIR / f"{page['slug']}.md"
        manifest_path = OUT_DIR / f"{page['slug']}.images.json"

        out_path.write_text(
            f"# {page['title']}\n\n" + "\n".join(body).strip() + "\n",
            encoding="utf-8",
        )
        manifest_path.write_text(
            json.dumps(image_entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"exported {out_path}")


if __name__ == "__main__":
    main()
