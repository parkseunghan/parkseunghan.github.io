from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
POSTS_DIR = ROOT / "_posts" / "security-academy"


SCHEDULE = {
    1: ("2026-03-03", "18:00:00"),
    2: ("2026-03-03", "18:10:00"),
    3: ("2026-03-09", "18:00:00"),
    4: ("2026-03-09", "18:10:00"),
    5: ("2026-03-14", "18:00:00"),
    6: ("2026-03-14", "18:10:00"),
    7: ("2026-03-16", "18:00:00"),
    8: ("2026-03-16", "18:10:00"),
    9: ("2026-03-16", "18:20:00"),
    10: ("2026-03-22", "18:00:00"),
    11: ("2026-03-22", "18:10:00"),
    12: ("2026-03-22", "18:20:00"),
    13: ("2026-03-25", "18:00:00"),
    14: ("2026-03-25", "18:10:00"),
    15: ("2026-03-25", "18:20:00"),
}


def extract_index(path: Path) -> int:
    match = re.match(r"\d{4}-\d{2}-\d{2}-security-academy-(\d+)-", path.name)
    if not match:
        raise ValueError(f"unexpected filename: {path.name}")
    return int(match.group(1))


def update_front_matter(text: str, timestamp: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("front matter not found")
    date_line = f"date: {timestamp}\n"
    last_modified_line = f"last_modified_at: {timestamp}\n"

    if re.search(r"^date: .*$", text, re.MULTILINE):
        text = re.sub(r"^date: .*$", date_line.rstrip("\n"), text, flags=re.MULTILINE)
    else:
        text = re.sub(r"^(title: .*\n)", r"\1" + date_line, text, count=1, flags=re.MULTILINE)

    if re.search(r"^last_modified_at: .*$", text, re.MULTILINE):
        text = re.sub(
            r"^last_modified_at: .*$",
            last_modified_line.rstrip("\n"),
            text,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(r"^published: .*$", last_modified_line + r"published: false", text, flags=re.MULTILINE)

    return text


def main() -> None:
    paths = sorted(POSTS_DIR.glob("*.md"))
    rename_pairs: list[tuple[Path, Path]] = []

    for path in paths:
        index = extract_index(path)
        day, time = SCHEDULE[index]
        timestamp = f"{day}T{time}+09:00"
        text = path.read_text(encoding="utf-8")
        updated = update_front_matter(text, timestamp)
        path.write_text(updated, encoding="utf-8")

        suffix = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.name)
        new_path = path.with_name(f"{day}-{suffix}")
        rename_pairs.append((path, new_path))

    for old_path, new_path in rename_pairs:
        if old_path != new_path:
            old_path.rename(new_path)


if __name__ == "__main__":
    main()
