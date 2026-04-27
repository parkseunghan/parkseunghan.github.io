from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
POST_DIRS = [ROOT / "_posts" / "kisa-academy", ROOT / "_posts" / "security-academy"]


def has_hangul(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def is_ascii_term(text: str) -> bool:
    return bool(text) and all(ord(ch) < 128 for ch in text)


def is_acronym(text: str) -> bool:
    cleaned = re.sub(r"[^A-Za-z]", "", text)
    return bool(cleaned) and cleaned.isupper() and len(cleaned) <= 10


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def same_term(a: str, b: str) -> bool:
    norm = lambda s: re.sub(r"[\s,()_-]+", "", s).lower()
    return bool(a and b) and norm(a) == norm(b)


def choose_label(col1: str, col2: str) -> str:
    left = clean(col1)
    right = clean(col2)

    if not left:
        return right
    if not right:
        return left
    if same_term(left, right):
        return left

    left_hangul = has_hangul(left)
    right_hangul = has_hangul(right)

    if left_hangul and not right_hangul:
        return f"{right}({left})"
    if right_hangul and not left_hangul:
        return f"{left}({right})"
    if is_acronym(left) and not is_acronym(right):
        return f"{left}({right})"
    if is_acronym(right) and not is_acronym(left):
        return f"{right}({left})"
    if is_ascii_term(right) and not is_ascii_term(left):
        return f"{right}({left})"
    if is_ascii_term(left) and not is_ascii_term(right):
        return f"{left}({right})"
    return f"{left}({right})"


def row_to_bullet(line: str) -> str | None:
    if not line.startswith("|") or line.startswith("| ---") or "한글" in line:
        return None
    parts = [part.strip() for part in line.strip().strip("|").split("|")]
    if len(parts) < 4:
        return None
    term = choose_label(parts[0], parts[1])
    desc = clean(parts[2])
    extra = clean(parts[3])
    if extra:
        if extra.startswith("연관 키워드:") or extra.startswith("예:"):
            desc = f"{desc}. {extra}" if desc else extra
        else:
            desc = f"{desc}. {extra}" if desc else extra
    desc = desc.strip().rstrip(".")
    return f"- `{term}`: {desc}"


def convert_glossary_tables(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if line.strip() == "## 용어 정리":
            i += 1
            # keep blank line after heading
            while i < len(lines) and not lines[i].strip():
                i += 1
            bullets: list[str] = []
            while i < len(lines) and not lines[i].startswith("## "):
                bullet = row_to_bullet(lines[i])
                if bullet:
                    bullets.append(bullet)
                i += 1
            out.append("")
            if bullets:
                out.extend(bullets)
            out.append("")
            continue
        i += 1
    return "\n".join(out) + "\n"


def main() -> None:
    for post_dir in POST_DIRS:
        for path in sorted(post_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8").lstrip("\ufeff")
            updated = convert_glossary_tables(text)
            path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
