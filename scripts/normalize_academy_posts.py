from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
KISA_DIR = ROOT / "_posts" / "kisa-academy"
SECURITY_DIR = ROOT / "_posts" / "security-academy"


TITLE_PREFIX_OLD = '[TIL] KISA 아카데미 - '
TITLE_PREFIX_MID = 'KISA 아카데미 - '
TITLE_PREFIX_NEW = 'KISA 아카데미 정리 - '
META_PATTERNS = (
    "노션 메모",
    "강의교재",
    "이 글은",
    "재정리함",
)

KISA_CATEGORY_MAP = {
    "reversing": "Reverse Engineering",
    "malware": "Malware Analysis",
    "yara": "Malware Analysis",
    "spearphishing": "Malware Analysis",
    "shellcode": "Reverse Engineering",
}

SECURITY_CATEGORY_MAP = [
    ("security-academy-1-", "Programming"),
    ("security-academy-2-", "Programming"),
    ("security-academy-3-", "Infrastructure"),
    ("security-academy-4-", "Infrastructure"),
    ("security-academy-5-", "Programming"),
    ("security-academy-6-", "Programming"),
    ("security-academy-7-", "Infrastructure"),
    ("security-academy-8-", "Infrastructure"),
    ("security-academy-9-", "Infrastructure"),
    ("security-academy-10-", "Infrastructure"),
    ("security-academy-11-", "Infrastructure"),
    ("security-academy-12-", "Infrastructure"),
    ("security-academy-13-", "Infrastructure"),
    ("security-academy-14-", "Infrastructure"),
    ("security-academy-15-", "Infrastructure"),
]


def split_front_matter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        raise ValueError("front matter not found")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("front matter closing marker not found")
    return text[: end + 5], text[end + 5 :]


def replace_categories(front_matter: str, categories: list[str]) -> str:
    category_block = "categories:\n" + "".join(f"  - {category}\n" for category in categories)
    return re.sub(
        r'^categories:\n(?:  - .*\n)+',
        category_block,
        front_matter,
        flags=re.MULTILINE,
    )


def infer_kisa_categories(stem: str) -> list[str]:
    for key, category in KISA_CATEGORY_MAP.items():
        if f"-{key}-" in f"-{stem}-":
            return [category]
    return ["Malware Analysis"]


def infer_security_categories(stem: str) -> list[str]:
    for prefix, category in SECURITY_CATEGORY_MAP:
        if prefix in stem:
            return [category]
    return ["Infrastructure"]


def update_kisa_front_matter(front_matter: str, stem: str) -> str:
    title_match = re.search(r'^title: "(.*)"$', front_matter, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
        if title.startswith(TITLE_PREFIX_OLD):
            title = TITLE_PREFIX_NEW + title[len(TITLE_PREFIX_OLD) :]
        elif title.startswith(TITLE_PREFIX_MID):
            title = TITLE_PREFIX_NEW + title[len(TITLE_PREFIX_MID) :]
        front_matter = re.sub(
            r'^title: ".*"$',
            f'title: "{title}"',
            front_matter,
            flags=re.MULTILINE,
        )

    front_matter = replace_categories(front_matter, infer_kisa_categories(stem))

    permalink = f"/security-academy/{stem}/"
    if re.search(r"^permalink: ", front_matter, re.MULTILINE):
        front_matter = re.sub(
            r"^permalink: .*$",
            f"permalink: {permalink}",
            front_matter,
            flags=re.MULTILINE,
        )
    else:
        front_matter = front_matter.replace("\n---\n", f"\npermalink: {permalink}\n---\n")

    return front_matter


def update_security_front_matter(front_matter: str, stem: str) -> str:
    front_matter = replace_categories(front_matter, infer_security_categories(stem))
    front_matter = re.sub(
        r'^tags:\n  - Security Academy\n',
        "tags:\n  - Security Academy 7th\n",
        front_matter,
        flags=re.MULTILINE,
    )
    return front_matter


def parse_glossary_bullet(content: str) -> tuple[str, str, str, str]:
    line = content.strip()
    if line.startswith("- "):
        line = line[2:].strip()

    term_part, sep, desc = line.partition(":")
    if not sep:
        term_part = line
        desc = ""
    term_part = term_part.strip()
    desc = desc.strip()

    terms = [part.strip() for part in term_part.split(" / ")]
    cleaned_terms = [term.strip("`") for term in terms if term]

    korean = cleaned_terms[0] if cleaned_terms else ""
    english = cleaned_terms[1] if len(cleaned_terms) > 1 else ""

    if len(cleaned_terms) == 1 and re.fullmatch(r"[A-Za-z0-9 .&()+_-]+", cleaned_terms[0]):
        english = cleaned_terms[0]

    related = ""
    if "연관 키워드:" in desc:
        desc, _, tail = desc.partition("연관 키워드:")
        desc = desc.strip()
        related = f"연관 키워드: {tail.strip()}"
    elif "예:" in desc:
        desc, _, tail = desc.partition("예:")
        desc = desc.strip()
        related = f"예: {tail.strip()}"

    return korean, english, desc, related


def make_glossary_table(lines: list[str]) -> list[str]:
    rows = [parse_glossary_bullet(line) for line in lines if line.strip()]
    table = [
        "| 한글 | 영문 | 설명 | 예시 및 연관 키워드 |",
        "| --- | --- | --- | --- |",
    ]

    def esc(value: str) -> str:
        return value.replace("|", "\\|")

    for korean, english, desc, related in rows:
        table.append(f"| {esc(korean)} | {esc(english)} | {esc(desc)} | {esc(related)} |")
    return table


def simplify_glossary_cell(text: str) -> str:
    value = text.strip()
    if not value:
        return value

    replacements = [
        ("에 해당함.", ""),
        ("에 해당함", ""),
        ("를 의미함.", ""),
        ("를 의미함", ""),
        ("을 의미함.", ""),
        ("을 의미함", ""),
        ("를 가리키는 개념임.", "를 가리키는 개념"),
        ("를 가리키는 개념임", "를 가리키는 개념"),
        ("를 가리키는 포인터임.", "를 가리키는 포인터"),
        ("를 가리키는 포인터임", "를 가리키는 포인터"),
        ("를 담고 있는 구조체임.", "를 담고 있는 구조체"),
        ("를 담는 구조체임.", "를 담는 구조체"),
        ("을 담고 있는 구조체임.", "을 담고 있는 구조체"),
        ("를 담고 있는 라이브러리임.", "를 담고 있는 라이브러리"),
        ("을 담고 있는 라이브러리임.", "을 담고 있는 라이브러리"),
        ("을 수행하는 도구 또는 프로그램에 해당함.", "을 수행하는 도구 또는 프로그램"),
        ("을 수행하는 도구 또는 프로그램에 해당함", "을 수행하는 도구 또는 프로그램"),
        ("임.", ""),
        ("임", ""),
    ]
    for old, new in replacements:
        if value.endswith(old):
            value = value[: -len(old)] + new
            break

    value = value.rstrip(". ")
    value = re.sub(r"\s{2,}", " ", value)
    return value


def simplify_glossary_tables(body: str) -> str:
    lines = body.splitlines()
    result: list[str] = []
    in_glossary = False
    for line in lines:
        if line.startswith("## 용어 정리"):
            in_glossary = True
            result.append(line)
            continue
        if in_glossary and line.startswith("## "):
            in_glossary = False
            result.append(line)
            continue
        if in_glossary and line.startswith("|") and not line.startswith("| ---"):
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 6 and parts[1] != "한글":
                if not parts[4]:
                    desc_parts = re.split(r"\.\s+", parts[3], maxsplit=1)
                    if len(desc_parts) == 2:
                        parts[3], parts[4] = desc_parts[0], desc_parts[1]
                parts[3] = simplify_glossary_cell(parts[3])
                parts[4] = simplify_glossary_cell(parts[4])
                line = "| " + " | ".join(parts[1:5]) + " |"
        result.append(line)
    return "\n".join(result)


def remove_meta_paragraphs(body: str) -> str:
    paragraphs = re.split(r"\n\s*\n", body.strip("\n"))
    kept: list[str] = []
    for paragraph in paragraphs:
        normalized = paragraph.strip()
        if any(pattern in normalized for pattern in META_PATTERNS):
            continue
        kept.append(paragraph)
    if not kept:
        return ""
    return "\n\n".join(kept) + "\n"


def normalize_glossary_section(body: str) -> str:
    match = re.search(r"^## 용어 정리\n", body, re.MULTILINE)
    if not match:
        return body

    section_start = match.end()
    next_match = re.search(r"^## ", body[section_start:], re.MULTILINE)
    section_end = section_start + next_match.start() if next_match else len(body)
    section = body[section_start:section_end]

    stripped_lines = [line for line in section.strip("\n").splitlines()]
    non_blank = [line for line in stripped_lines if line.strip()]
    if not non_blank:
        return body
    if non_blank[0].startswith("|"):
        return body
    if not all(line.lstrip().startswith("- ") for line in non_blank):
        return body

    new_section = "\n" + "\n".join(make_glossary_table(non_blank)) + "\n\n"
    return body[:section_start] + new_section + body[section_end:]


def cleanup_body(body: str) -> str:
    lines = body.splitlines()
    cleaned: list[str] = []
    for line in lines:
        if line.strip() == "|":
            continue
        cleaned.append(line)
    body = "\n".join(cleaned)
    body = remove_meta_paragraphs(body)
    body = simplify_glossary_tables(body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body + ("\n" if not body.endswith("\n") else "")


def process_markdown(path: Path, is_kisa: bool) -> None:
    text = path.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(text)

    if is_kisa:
        body = re.sub(r"^permalink: .*\n+", "", body)
        front_matter = update_kisa_front_matter(front_matter, path.stem)
    else:
        front_matter = update_security_front_matter(front_matter, path.stem)

    body = cleanup_body(body)
    body = normalize_glossary_section(body)
    body = simplify_glossary_tables(body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = body + ("\n" if not body.endswith("\n") else "")

    path.write_text(front_matter + body, encoding="utf-8")


def main() -> None:
    for path in sorted(KISA_DIR.glob("*.md")):
        process_markdown(path, is_kisa=True)
    for path in sorted(SECURITY_DIR.glob("*.md")):
        process_markdown(path, is_kisa=False)


if __name__ == "__main__":
    main()
