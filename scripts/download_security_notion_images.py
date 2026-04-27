import json
import re
import urllib.request
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\01seu\parkseunghan.github.io")
SOURCE_DIR = REPO_ROOT / "tmp" / "security-academy-source"
OUTPUT_ROOT = REPO_ROOT / "assets" / "images" / "writeup" / "security-academy" / "notion"


def sanitize_stem(value: str) -> str:
    value = value.strip()
    value = re.sub(r'[<>:"/\\\\|?*]+', "-", value)
    value = re.sub(r"\s+", "-", value)
    value = value.strip("-.")
    return value or "image"


def ext_from_url(url: str) -> str:
    lower = url.lower()
    for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]:
        if ext in lower:
            return ext
    return ".png"


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifests = sorted(SOURCE_DIR.glob("*.images.json"))
    for manifest_path in manifests:
        key = manifest_path.stem.replace(".images", "")
        items = json.loads(manifest_path.read_text(encoding="utf-8"))
        out_dir = OUTPUT_ROOT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []
        seen = set()

        for idx, item in enumerate(items, start=1):
            url = item.get("source_url") or ""
            if not url:
                continue
            stem = sanitize_stem(item.get("marker") or f"{key}-{idx:03d}")
            ext = ext_from_url(url)
            filename = f"{stem}{ext}"
            suffix = 2
            while filename.lower() in seen:
                filename = f"{stem}-{suffix}{ext}"
                suffix += 1
            seen.add(filename.lower())
            dest = out_dir / filename
            with urllib.request.urlopen(url) as response, dest.open("wb") as fh:
                fh.write(response.read())
            downloaded.append(
                {
                    "sequence": idx,
                    "filename": filename,
                    "marker": item.get("marker"),
                    "caption": item.get("caption"),
                    "source_url": url,
                    "block_id": item.get("block_id"),
                }
            )

        (out_dir / "index.json").write_text(
            json.dumps(downloaded, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"{key}: {len(downloaded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
