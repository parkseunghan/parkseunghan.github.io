import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
CODEX_EXE = Path(r"C:\Users\01seu\.codex\.sandbox-bin\codex.exe")
OUTPUT_ROOT = REPO_ROOT / "assets" / "images" / "writeup" / "kisa-academy" / "notion"
LOG_ROOT = REPO_ROOT / "logs" / "kisa-image-download"

PAGES = [
    {
        "page_id": "185b8597-ec48-807e-8d84-efb05b881d67",
        "page_key": "reversing",
    },
    {
        "page_id": "188b8597-ec48-80bc-b104-de36d5ae1b0b",
        "page_key": "malware",
    },
    {
        "page_id": "191b8597-ec48-8070-b21d-f2bdec2365fa",
        "page_key": "yara",
    },
    {
        "page_id": "196b8597-ec48-80c2-b476-d9b57b979329",
        "page_key": "spearphishing",
    },
    {
        "page_id": "198b8597-ec48-8071-a6e0-dd84c94addf7",
        "page_key": "shellcode",
    },
]

PROMPT_TEMPLATE = """Use the authenticated Notion MCP tool.
Fetch page id {page_id}.
Do not search, browse, or inspect any local files.
After the fetch succeeds, reply with exactly one line:
FETCH_OK
"""


def summarize_output(output_dir: Path) -> tuple[int, int]:
    image_count = len([p for p in output_dir.iterdir() if p.is_file() and p.name != "index.json"])
    index_count = 0
    index_path = output_dir / "index.json"
    if index_path.exists():
        try:
            index_count = len(json.loads(index_path.read_text(encoding="utf-8-sig")))
        except Exception:
            index_count = -1
    return image_count, index_count


def sanitize_stem(value: str) -> str:
    value = re.sub(r"\[이미지:(.+?)\]", r"\1", value)
    value = value.strip()
    value = re.sub(r'[<>:"/\\\\|?*]+', "-", value)
    value = re.sub(r"\s+", "-", value)
    value = value.strip("-.")
    return value or "image"


def extract_fetch_payload(log_text: str) -> str:
    marker = "notion.notion-fetch("
    success_idx = log_text.find("success in", log_text.find(marker))
    if success_idx == -1:
        raise ValueError("notion fetch success block not found")

    json_start = log_text.find("\n{", success_idx)
    if json_start == -1:
        raise ValueError("tool JSON start not found")
    json_start += 1

    decoder = json.JSONDecoder()
    payload, _ = decoder.raw_decode(log_text[json_start:])
    raw_text = payload["content"][0]["text"]
    page_blob = json.loads(raw_text)
    return page_blob["text"]


def build_items(page_text: str, page_key: str) -> list[dict]:
    items: list[dict] = []
    current_marker = None
    recent_texts: list[str] = []
    auto_index = 1
    used_names: set[str] = set()

    for raw_line in page_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        marker_match = re.search(r"\[이미지:(.+?)\]", line)
        if marker_match:
            current_marker = marker_match.group(1).strip()
            continue

        image_match = re.search(r"!\[[^\]]*\]\((https?://[^)]+)\)", line)
        if image_match:
            source_url = image_match.group(1)
            caption = ""
            for candidate in reversed(recent_texts[-3:]):
                if not candidate.startswith("![](") and "[이미지:" not in candidate:
                    caption = candidate
                    break

            if current_marker:
                stem = sanitize_stem(current_marker)
            else:
                stem = f"{page_key}-{auto_index:03d}"
                auto_index += 1

            filename = f"{stem}.png"
            suffix = 2
            while filename.lower() in used_names:
                filename = f"{stem}-{suffix}.png"
                suffix += 1
            used_names.add(filename.lower())

            items.append(
                {
                    "sequence": len(items) + 1,
                    "filename": filename,
                    "marker": current_marker,
                    "caption": caption,
                    "source_url": source_url,
                }
            )
            current_marker = None
            continue

        if not line.startswith("<") and not line.startswith("{") and not line.startswith("Here is the result"):
            recent_texts.append(line)

    return items


def download_items(items: list[dict], output_dir: Path) -> None:
    for item in items:
        dest = output_dir / item["filename"]
        with urllib.request.urlopen(item["source_url"]) as response, dest.open("wb") as fh:
            fh.write(response.read())

    (output_dir / "index.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def snapshot(output_dir: Path) -> tuple[int, int, int]:
    files = sorted(p for p in output_dir.iterdir() if p.is_file())
    count = len(files)
    total_size = sum(p.stat().st_size for p in files)
    newest = max((int(p.stat().st_mtime) for p in files), default=0)
    return count, total_size, newest


def terminate_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)


def run_page(page: dict) -> bool:
    output_dir = OUTPUT_ROOT / page["page_key"]
    log_path = LOG_ROOT / f"{page['page_key']}.log"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = PROMPT_TEMPLATE.format(page_id=page["page_id"])

    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        proc = subprocess.Popen(
            [
                str(CODEX_EXE),
                "exec",
                "--skip-git-repo-check",
                "--dangerously-bypass-approvals-and-sandbox",
                "-C",
                str(REPO_ROOT),
                prompt,
            ],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        start = time.time()
        max_wait = 15 * 60

        while time.time() - start < max_wait:
            time.sleep(5)
            if proc.poll() is not None:
                break

        if proc.poll() is None:
            terminate_process(proc)

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    try:
        page_text = extract_fetch_payload(log_text)
        items = build_items(page_text, page["page_key"])
        download_items(items, output_dir)
    except Exception as exc:
        print(f"{page['page_key']}: parse/download failed: {exc}", file=sys.stderr)
        items = []

    image_count, index_count = summarize_output(output_dir)
    print(f"{page['page_key']}: files={image_count}, index={index_count}, log={log_path}")
    return image_count > 0 and index_count > 0 and image_count == index_count == len(items)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pages",
        nargs="*",
        help="page_key values to run, e.g. malware yara",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)

    if not CODEX_EXE.exists():
        print(f"Missing codex executable: {CODEX_EXE}", file=sys.stderr)
        return 1

    selected = PAGES
    if args.pages:
        wanted = set(args.pages)
        selected = [page for page in PAGES if page["page_key"] in wanted]
        missing = sorted(wanted - {page["page_key"] for page in selected})
        if missing:
            print("UNKNOWN_PAGES: " + ", ".join(missing), file=sys.stderr)
            return 1

    failures = []
    for page in selected:
        print(f"[START] {page['page_key']}")
        ok = run_page(page)
        if not ok:
            failures.append(page["page_key"])
            print(f"[FAIL] {page['page_key']}")
        else:
            print(f"[DONE] {page['page_key']}")

    if failures:
        print("FAILED: " + ", ".join(failures), file=sys.stderr)
        return 1

    print("ALL_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
