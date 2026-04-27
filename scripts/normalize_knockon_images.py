from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_TIL = Path(r"C:\Users\01seu\Downloads\knock-on-til-master\knock-on-til-master")
CHALLENGE_IMG_DIR = ROOT / "assets" / "images" / "writeup" / "web-hacking" / "knock-on"
TIL_IMG_DIR = ROOT / "assets" / "images" / "writeup" / "web-architecture" / "knock-on-til"


TIL_IMAGE_MAP = {
    "2024-08-01-프로토콜.md": [
        ("./assets/images/ipv4_데이터그램포맷.png", "knock-on-til-protocol-01.png"),
        ("./assets/images/ipv6_데이터그램포맷.png", "knock-on-til-protocol-02.png"),
    ],
    "2024-08-04-Cookie_Session-Challenge.md": [
        ("./assets/images/naver(2).png", "knock-on-til-cookie-session-challenge-01.png"),
        ("./assets/images/naver(1).png", "knock-on-til-cookie-session-challenge-02.png"),
    ],
    "2024-08-05-패킷-Challenge.md": [
        ("./assets/images/패킷(1).png", "knock-on-til-packet-challenge-01.png"),
        ("./assets/images/패킷(2).png", "knock-on-til-packet-challenge-02.png"),
        ("./assets/images/패킷(3).png", "knock-on-til-packet-challenge-03.png"),
        ("./assets/images/패킷(4).png", "knock-on-til-packet-challenge-04.png"),
    ],
    "2024-08-06-html_css_js-Challenge.md": [
        ("./assets/images/자기소개.png", "knock-on-til-html-css-js-challenge-01.png"),
        ("./assets/images/계산기.png", "knock-on-til-html-css-js-challenge-02.png"),
        ("./assets/images/계산기2.png", "knock-on-til-html-css-js-challenge-03.png"),
    ],
    "2024-08-07-html-Challenge.md": [
        ("./assets/images/peach.png", "knock-on-til-html-challenge-01.png"),
        ("./assets/images/strawberry.png", "knock-on-til-html-challenge-02.png"),
    ],
    "2024-08-07-javascript-Challenge.md": [
        ("./assets/images/룰렛1.png", "knock-on-til-javascript-challenge-01.png"),
        ("./assets/images/룰렛2.png", "knock-on-til-javascript-challenge-02.png"),
        ("./assets/images/룰렛3.png", "knock-on-til-javascript-challenge-03.png"),
        ("./assets/images/룰렛4.png", "knock-on-til-javascript-challenge-04.png"),
    ],
    "2024-08-08-apache-Challenge.md": [
        ("./assets/images/아파치1.png", "knock-on-til-apache-challenge-01.png"),
        ("./assets/images/아파치2.png", "knock-on-til-apache-challenge-02.png"),
        ("./assets/images/아파치3.png", "knock-on-til-apache-challenge-03.png"),
        ("./assets/images/아파치4.png", "knock-on-til-apache-challenge-04.png"),
        ("./assets/images/아파치5.png", "knock-on-til-apache-challenge-05.png"),
        ("./assets/images/아파치6.png", "knock-on-til-apache-challenge-06.png"),
        ("./assets/images/아파치7.png", "knock-on-til-apache-challenge-07.png"),
        ("./assets/images/AWS_EC2_1.png", "knock-on-til-apache-challenge-08.png"),
        ("./assets/images/AWS_EC2_2.png", "knock-on-til-apache-challenge-09.png"),
        ("./assets/images/AWS_EC2_3.png", "knock-on-til-apache-challenge-10.png"),
        ("./assets/images/AWS_EC2_4.png", "knock-on-til-apache-challenge-11.png"),
        ("./assets/images/AWS_EC2_5.png", "knock-on-til-apache-challenge-12.png"),
        ("./assets/images/AWS_EC2_6.png", "knock-on-til-apache-challenge-13.png"),
        ("./assets/images/AWS_EC2_7.png", "knock-on-til-apache-challenge-14.png"),
        ("./assets/images/AWS_EC2_8.png", "knock-on-til-apache-challenge-15.png"),
        ("./assets/images/AWS_EC2_9.png", "knock-on-til-apache-challenge-16.png"),
        ("./assets/images/AWS_EC2_10.png", "knock-on-til-apache-challenge-17.png"),
        ("./assets/images/AWS_EC2_11.png", "knock-on-til-apache-challenge-18.png"),
        ("./assets/images/AWS_EC2_12.png", "knock-on-til-apache-challenge-19.png"),
    ],
    "2024-08-10-mysql-Challenge.md": [
        ("./assets/images/sql1.png", "knock-on-til-mysql-challenge-01.png"),
        ("./assets/images/sql2.png", "knock-on-til-mysql-challenge-02.png"),
        ("./assets/images/sql3.png", "knock-on-til-mysql-challenge-03.png"),
        ("./assets/images/sql4.png", "knock-on-til-mysql-challenge-04.png"),
        ("./assets/images/sql5.png", "knock-on-til-mysql-challenge-05.png"),
        ("./assets/images/sql6.png", "knock-on-til-mysql-challenge-06.png"),
        ("./assets/images/sql7.png", "knock-on-til-mysql-challenge-07.png"),
        ("./assets/images/sql8.png", "knock-on-til-mysql-challenge-08.png"),
        ("./assets/images/sql9.png", "knock-on-til-mysql-challenge-09.png"),
        ("./assets/images/join1.png", "knock-on-til-mysql-challenge-10.png"),
        ("./assets/images/join2.png", "knock-on-til-mysql-challenge-11.png"),
        ("./assets/images/join3.png", "knock-on-til-mysql-challenge-12.png"),
        ("./assets/images/join4.png", "knock-on-til-mysql-challenge-13.png"),
    ],
    "2024-08-11-php-Challenge.md": [
        ("./assets/images/php1.png", "knock-on-til-php-challenge-01.png"),
    ],
}


def slugify_stem(stem: str) -> str:
    stem = stem.lower().replace("_", "-")
    stem = re.sub(r"[^a-z0-9-]+", "-", stem)
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return f"knock-on-challenge-{stem}"


def rename_challenge_images() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in sorted(CHALLENGE_IMG_DIR.glob("*.*")):
        new_name = f"{slugify_stem(path.stem)}{path.suffix.lower()}"
        target = path.with_name(new_name)
        if path.name != new_name:
            path.rename(target)
        mapping[path.name] = new_name
    return mapping


def update_challenge_post_refs(mapping: dict[str, str]) -> None:
    for post in list((ROOT / "_posts" / "knock-on-challenges").glob("*.md")) + list((ROOT / "_posts" / "webhacking-kr").glob("*.md")):
        text = post.read_text(encoding="utf-8")
        original = text
        for old, new in mapping.items():
            text = text.replace(f"/assets/images/writeup/web-hacking/knock-on/{old}", f"/assets/images/writeup/web-hacking/knock-on/{new}")
        if text != original:
            post.write_text(text, encoding="utf-8")


def import_til_images() -> None:
    TIL_IMG_DIR.mkdir(parents=True, exist_ok=True)
    src_img_dir = SRC_TIL / "assets" / "images"
    posts_dir = ROOT / "_posts" / "knock-on-til"

    for post_name, items in TIL_IMAGE_MAP.items():
        post_path = posts_dir / post_name
        text = post_path.read_text(encoding="utf-8")
        original = text
        for old_rel, new_name in items:
            src_name = old_rel.split("/")[-1]
            src_path = src_img_dir / src_name
            dst_path = TIL_IMG_DIR / new_name
            shutil.copy2(src_path, dst_path)
            text = text.replace(old_rel, f"/assets/images/writeup/web-architecture/knock-on-til/{new_name}")
        if text != original:
            post_path.write_text(text, encoding="utf-8")


def main() -> None:
    mapping = rename_challenge_images()
    update_challenge_post_refs(mapping)
    import_til_images()


if __name__ == "__main__":
    main()
