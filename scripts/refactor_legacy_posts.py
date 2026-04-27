from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def split_front_matter(text: str) -> tuple[str, str, str]:
    if not text.startswith("---\n"):
        return "", "", text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return "", "", text
    return "---\n", parts[1], parts[2]


def strip_title_prefix(fm: str, *, challenge: bool) -> str:
    replacements = {
        '[Writeup] ': '',
        '[TIL] ': '',
        '[TIL Challenge] ': '',
    }
    for old, new in replacements.items():
        fm = fm.replace(f'title: "{old}', 'title: "')
    if challenge:
        fm = re.sub(
            r'^title: "([^"]+?)(?:\s*실습)?"$',
            lambda m: f'title: "{m.group(1)} 실습"',
            fm,
            flags=re.MULTILINE,
        )
    return fm


def normalize_body(text: str, *, writeup: bool, til: bool) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False

    heading_map = {
        "## Exploit": "## 풀이",
        "## Explot": "## 풀이",
        "## Payload": "## 페이로드",
        "## payload": "## 페이로드",
        "## References": "## 참고",
    }

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue

        if not in_fence and stripped == "|":
            continue

        if not in_fence and stripped == "---":
            continue

        if writeup and not in_fence:
            line = heading_map.get(line, line)

        if til and not in_fence and line.startswith("# "):
            line = "## " + line[2:]

        out.append(line.rstrip())

    text = "\n".join(out).strip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def refactor_file(path: Path, *, writeup: bool = False, til: bool = False, challenge: bool = False) -> None:
    original = path.read_text(encoding="utf-8")
    begin, fm, body = split_front_matter(original)
    if begin:
        fm = strip_title_prefix(fm, challenge=challenge)
        body = normalize_body(body, writeup=writeup, til=til)
        updated = begin + fm + "---\n" + body
    else:
        updated = normalize_body(original, writeup=writeup, til=til)

    if updated != original:
        path.write_text(updated, encoding="utf-8")


def main() -> None:
    for path in sorted((ROOT / "_posts" / "webhacking-kr").glob("*.md")):
        refactor_file(path, writeup=True)

    for path in sorted((ROOT / "_posts" / "knock-on-challenges").glob("*.md")):
        refactor_file(path, writeup=True)

    for path in sorted((ROOT / "_posts" / "knock-on-til").glob("*.md")):
        refactor_file(path, til=True, challenge="Challenge" in path.name)


if __name__ == "__main__":
    main()
