"""Scrape 春秋穀梁传 from Wikisource → unified schema.

Wikisource has 12 chapter pages, one per 公 — much cleaner than ctext.org
(which rate-limits unauthenticated API users after ~50 requests).
Source: https://zh.wikisource.org/wiki/春秋穀梁傳/<duke>
"""

import json
import re
import time
import html
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from opencc import OpenCC

T2S = OpenCC("t2s")  # traditional → simplified, matches the rest of the corpus

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "output" / "shisanjing" / "guliang.json"

UA = "classical-corpus/0.4 (https://github.com/zionq) personal research"

# 12 公 (traditional Chinese names as Wikisource uses)
DUKES = [
    ("隱公", "隐公"),
    ("桓公", "桓公"),
    ("莊公", "庄公"),
    ("閔公", "闵公"),
    ("僖公", "僖公"),
    ("文公", "文公"),
    ("宣公", "宣公"),
    ("成公", "成公"),
    ("襄公", "襄公"),
    ("昭公", "昭公"),
    ("定公", "定公"),
    ("哀公", "哀公"),
]

DELAY = 1.0


def http_get(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_duke(trad_name: str) -> str:
    """Fetch and clean one 公's page content."""
    url = f"https://zh.wikisource.org/wiki/{quote('春秋穀梁傳')}/{quote(trad_name)}"
    raw = http_get(url)
    # strip tags
    notags = re.sub(r"<[^>]+>", " ", raw)
    notags = html.unescape(notags)
    # extract Chinese-rich chunks only (drops nav/header/footer)
    chunks = re.findall(r"[一-鿿，。：；「」『』《》、！？（）]{20,}", notags)
    body = "\n\n".join(chunks)
    return T2S.convert(body)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out: list[dict] = []
    for i, (trad_name, simp_name) in enumerate(DUKES, 1):
        print(f"[{i:2d}/12] {simp_name} ({trad_name})...", end=" ", flush=True)
        try:
            body = fetch_duke(trad_name)
            print(f"{len(body):,} chars")
        except Exception as e:
            print(f"FAILED: {e}")
            body = ""
        out.append(
            {
                "id": f"guliang#{i}",
                "source": "春秋穀梁传",
                "author": "穀梁赤",
                "era": "战国",
                "category": "经",
                "chapter": simp_name,
                "section": i,
                "content": body,
            }
        )
        with OUTPUT.open("w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        time.sleep(DELAY)

    chars = sum(len(r["content"]) for r in out)
    print(f"\ndone: {len(out)} 公, {chars:,} 字  → {OUTPUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
