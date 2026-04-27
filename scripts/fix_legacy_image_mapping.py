from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REPLACEMENTS = {
    "_posts/knock-on-challenges/2024-08-24-knock-on-challenges-1-2.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_2.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_3.png",
        "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_4.png",
        "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_5.png",
        "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_4.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_6.png",
        "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_5.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_7.png",
        "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_6.png": "/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_8.png",
    },
    "_posts/knock-on-challenges/2024-08-25-knock-on-challenges-2.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_2.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_3.png",
    },
    "_posts/knock-on-challenges/2024-08-26-knock-on-challenges-2-1.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/2-1_What_time_is_it_2.png",
    },
    "_posts/knock-on-challenges/2024-08-28-knock-on-challenges-3-1.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/3-1_SQLi_WAF_1_1.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/3-1_SQLi_WAF_1_1.png",
    },
    "_posts/knock-on-challenges/2024-08-28-knock-on-challenges-3-2.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/3-2_SQLi_WAF_2_1.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/3-2_SQLi_WAF_2_2.png",
    },
    "_posts/knock-on-challenges/2024-08-29-knock-on-challenges-3-3.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/3-3_SQLi_WAF_3_1.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/3-3_SQLi_WAF_3_1.png",
    },
    "_posts/knock-on-challenges/2024-08-29-knock-on-challenges-3-4.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/3-4_SQLi_WAF_4_1.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/3-4_SQLi_WAF_4_1.png",
    },
    "_posts/knock-on-challenges/2024-08-30-knock-on-challenges-3-5.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/3-5_SQLi_WAF_5_1.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/3-5_SQLi_WAF_5_1.png",
    },
    "_posts/knock-on-challenges/2024-08-29-knock-on-challenges-3-6.md": {
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png": "/assets/images/writeup/web-hacking/knock-on/3-6_SQLi_WAF_6_1.png",
        "/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png": "/assets/images/writeup/web-hacking/knock-on/3-6_SQLi_WAF_6_1.png",
    },
    "_posts/knock-on-challenges/2024-09-08-knock-on-challenges-5-2.md": {
        "/assets/images/writeup/web-hacking/knock-on/5-1_XSS_2.png": "/assets/images/writeup/web-hacking/knock-on/5-2_XSS_1.png",
        "/assets/images/writeup/web-hacking/knock-on/5-1_XSS_3.png": "/assets/images/writeup/web-hacking/knock-on/5-2_XSS_1.png",
    },
    "_posts/knock-on-challenges/2024-09-09-knock-on-challenges-5-3.md": {
        "/assets/images/writeup/web-hacking/knock-on/5-1_XSS_2.png": "/assets/images/writeup/web-hacking/knock-on/5-3_XSS_1.png",
        "/assets/images/writeup/web-hacking/knock-on/5-1_XSS_3.png": "/assets/images/writeup/web-hacking/knock-on/5-3_XSS_1.png",
    },
    "_posts/knock-on-challenges/2024-09-09-knock-on-challenges-5-4.md": {
        "/assets/images/writeup/web-hacking/knock-on/5-1_XSS_2.png": "/assets/images/writeup/web-hacking/knock-on/5-4_XSS_1.png",
        "/assets/images/writeup/web-hacking/knock-on/5-1_XSS_3.png": "/assets/images/writeup/web-hacking/knock-on/5-4_XSS_1.png",
    },
    "_posts/knock-on-challenges/2024-09-12-knock-on-challenges-6-1.md": {
        "/assets/images/writeup/web-hacking/knock-on/6_XSS_2.png": "/assets/images/writeup/web-hacking/knock-on/6-1_XSS_2.png",
    },
    "_posts/knock-on-challenges/2024-09-13-knock-on-challenges-8-2.md": {
        "/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_2.png": "/assets/images/writeup/web-hacking/knock-on/8-2_SSTI_1.png",
        "/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_3.png": "/assets/images/writeup/web-hacking/knock-on/8-2_SSTI_2.png",
    },
    "_posts/knock-on-challenges/2024-09-16-knock-on-challenges-10-2.md": {
        "/assets/images/writeup/web-hacking/knock-on/10-1_FILE_2.png": "/assets/images/writeup/web-hacking/knock-on/10-2_FILE_2.png",
    },
    "_posts/knock-on-challenges/2024-09-16-knock-on-challenges-10-3.md": {
        "/assets/images/writeup/web-hacking/knock-on/10-1_FILE_2.png": "/assets/images/writeup/web-hacking/knock-on/10-3_FILE_2.png",
    },
}


def main() -> None:
    for rel, replacements in REPLACEMENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
