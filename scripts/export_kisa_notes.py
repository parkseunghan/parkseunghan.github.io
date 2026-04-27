import json
import re
import sqlite3
from pathlib import Path


DB_PATH = Path(r"C:\Users\01seu\AppData\Roaming\Notion\notion.db")
REPO_ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
POST_DIR = REPO_ROOT / "_posts" / "kisa-academy"
MANIFEST_DIR = REPO_ROOT / "assets" / "images" / "writeup" / "kisa-academy" / "notion-manifest"

PAGES = [
    {
        "page_id": "185b8597-ec48-807e-8d84-efb05b881d67",
        "slug": "kisa-reversing-notes",
        "date": "2025-01-24",
        "title": "KISA 아카데미 정리 - 리버싱",
        "last_modified_at": "2025-02-06T18:00:00+09:00",
        "tags": ["KISA Academy", "Reverse Engineering", "PE Format", "Windows Internals", "Assembly"],
    },
    {
        "page_id": "188b8597-ec48-80bc-b104-de36d5ae1b0b",
        "slug": "kisa-malware-notes",
        "date": "2025-01-27",
        "title": "KISA 아카데미 정리 - 멀웨어",
        "last_modified_at": "2025-02-06T18:00:00+09:00",
        "tags": ["KISA Academy", "Malware Analysis", "Dynamic Analysis", "Office Document", "PE Format"],
    },
    {
        "page_id": "191b8597-ec48-8070-b21d-f2bdec2365fa",
        "slug": "kisa-yara-notes",
        "date": "2025-02-05",
        "title": "KISA 아카데미 정리 - YARA",
        "last_modified_at": "2025-02-11T18:00:00+09:00",
        "tags": ["KISA Academy", "YARA", "Regex", "Triage", "IOC"],
    },
    {
        "page_id": "196b8597-ec48-80c2-b476-d9b57b979329",
        "slug": "kisa-spearphishing-notes",
        "date": "2025-02-05",
        "title": "KISA 아카데미 정리 - 스피어피싱",
        "last_modified_at": "2025-02-11T18:00:00+09:00",
        "tags": ["KISA Academy", "Spear Phishing", "MITRE ATT&CK", "Fileless", "LoLBin"],
    },
    {
        "page_id": "198b8597-ec48-8071-a6e0-dd84c94addf7",
        "slug": "kisa-shellcode-notes",
        "date": "2025-02-12",
        "title": "KISA 아카데미 정리 - 쉘코드",
        "last_modified_at": "2025-02-18T18:00:00+09:00",
        "tags": ["KISA Academy", "Shellcode", "PEB", "Windows Internals", "Assembly"],
    },
]

MARKER_RE = re.compile(r"\[이미지:(.+?)\]")


def load_blocks():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, type, properties, content, parent_id, format, file_ids "
        "FROM block WHERE alive=1 AND space_id='29af0f24-72d3-477f-a439-cccb346de9ee'"
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


def parse_json(value):
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def rich_text_to_md(spans):
    if not spans:
        return ""
    parts = []
    for span in spans:
        if not span:
            continue
        text = span[0] if isinstance(span, list) else str(span)
        marks = span[1] if isinstance(span, list) and len(span) > 1 else []
        text = text.replace("\u00a0", " ")
        href = None
        wrap_left = ""
        wrap_right = ""
        for mark in marks:
            if not mark:
                continue
            kind = mark[0]
            if kind == "c":
                wrap_left += "`"
                wrap_right = "`" + wrap_right
            elif kind == "b":
                wrap_left += "**"
                wrap_right = "**" + wrap_right
            elif kind == "i":
                wrap_left += "*"
                wrap_right = "*" + wrap_right
            elif kind == "s":
                wrap_left += "~~"
                wrap_right = "~~" + wrap_right
            elif kind == "a" and len(mark) > 1:
                href = mark[1]
        text = f"{wrap_left}{text}{wrap_right}"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts).strip()


def block_text(block, key="title"):
    props = block.get("properties") or {}
    return rich_text_to_md(props.get(key) or [])


def collect_descendants(blocks, root_id):
    out = []
    stack = [root_id]
    seen = set()
    while stack:
        block_id = stack.pop()
        if block_id in seen:
            continue
        seen.add(block_id)
        out.append(block_id)
        stack.extend(reversed(blocks.get(block_id, {}).get("content", [])))
    return out


def render_table(blocks, table_block):
    rows = []
    for row_id in table_block.get("content", []):
        props = blocks.get(row_id, {}).get("properties") or {}
        cells = props.get("title") or []
        rows.append([rich_text_to_md(cell if isinstance(cell, list) else [cell]) for cell in cells])
    if not rows:
        return []
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    header = rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
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

        if btype in {"header", "sub_header", "sub_sub_header", "toggle"}:
            level_map = {"header": 2, "sub_header": 3, "sub_sub_header": 4, "toggle": 2}
            level = max(2, level_map.get(btype, heading_base))
            title = text or "제목 없음"
            lines.append(f'{"#" * level} {title}')
            lines.append("")
            if block.get("content"):
                lines.extend(render_children(blocks, block["content"], image_entries, heading_base + 1))
            continue

        if btype == "bulleted_list":
            if text:
                lines.append(f"- {text}")
            if block.get("content"):
                for child_line in render_children(blocks, block["content"], image_entries, heading_base):
                    if child_line:
                        lines.append(f"  {child_line}")
                    else:
                        lines.append("")
            continue

        if btype == "numbered_list":
            if text:
                lines.append(f"1. {text}")
            if block.get("content"):
                for child_line in render_children(blocks, block["content"], image_entries, heading_base):
                    if child_line:
                        lines.append(f"   {child_line}")
                    else:
                        lines.append("")
            continue

        if btype == "code":
            language = ""
            props = block.get("properties") or {}
            lang_value = props.get("language") or []
            if lang_value:
                language = rich_text_to_md(lang_value).lower()
            code = block_text(block)
            lines.append(f"```{language}".rstrip())
            lines.append(code)
            lines.append("```")
            lines.append("")
            continue

        if btype == "divider":
            lines.append("---")
            lines.append("")
            continue

        if btype == "image":
            entry = {
                "block_id": block["id"],
                "marker": pending_marker,
                "caption": block_text(block, "caption"),
                "title": block_text(block),
                "source": block_text(block, "source"),
                "file_ids": block.get("file_ids") or [],
            }
            image_entries.append(entry)
            pending_image_idx = len(image_entries) - 1
            pending_marker = None
            continue

        if btype == "table":
            lines.extend(render_table(blocks, block))
            continue

        if btype in {"column_list", "column"}:
            if block.get("content"):
                lines.extend(render_children(blocks, block["content"], image_entries, heading_base))
            continue

        if btype in {"bookmark", "embed", "external_object_instance"}:
            source = block_text(block, "source") or block_text(block)
            caption = block_text(block, "caption")
            if source:
                lines.append(f"- 링크: {source}")
                if caption:
                    lines.append(f"  - 메모: {caption}")
            lines.append("")
            continue

        if block.get("content"):
            lines.extend(render_children(blocks, block["content"], image_entries, heading_base))

    if pending_image_idx is not None:
        entry = image_entries[pending_image_idx]
        label = entry["marker"] or "미지정"
        caption = entry["caption"] or "설명 없음"
        lines.append(f"> [이미지 대기] `{label}` - {caption}")

    return lines


def dump_post(page, blocks):
    page_block = blocks[page["page_id"]]
    image_entries = []
    body = [
        "> 노션 원문 기반 초안.",
        "> 문장은 최대한 원문을 유지했고, 이미지 파일은 노션 메타데이터만 먼저 저장했습니다.",
        "> [보강 필요] 표기된 부분만 이후에 손보면 됩니다.",
        "",
    ]
    body.extend(render_children(blocks, page_block.get("content", []), image_entries))
    body_text = "\n".join(trim_trailing_blank_lines(body)).strip() + "\n"

    front_matter = [
        "---",
        f'title: "{page["title"]}"',
        "categories:",
        "  - Malware Reversing",
        "tags:",
    ]
    for tag in page["tags"]:
        front_matter.append(f"  - {tag}")
    front_matter.extend(
        [
            f'permalink: /malware-reversing/{page["slug"]}/',
            f"last_modified_at: {page['last_modified_at']}",
            "published: false",
            "---",
            "",
        ]
    )

    post_path = POST_DIR / f"{page['date']}-{page['slug']}.md"
    post_path.write_text("\n".join(front_matter) + body_text, encoding="utf-8")

    manifest = {
        "page_id": page["page_id"],
        "title": page["title"],
        "image_count": len(image_entries),
        "images": image_entries,
    }
    manifest_path = MANIFEST_DIR / f"{page['slug']}.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def trim_trailing_blank_lines(lines):
    output = list(lines)
    while output and output[-1] == "":
        output.pop()
    return output


def main():
    POST_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    blocks = load_blocks()
    for page in PAGES:
        dump_post(page, blocks)
        print(f"WROTE {page['slug']}")


if __name__ == "__main__":
    main()
