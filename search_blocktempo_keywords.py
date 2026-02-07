import json
import os
from datetime import datetime

BASE_DIR = "output/news_history_multi/BlockTempo"
OUTPUT_DIR = "output/keyword_search"

KEYWORDS = [
    "elon musk",
    "elon",
    "馬斯克",
    "trump",
    "川普",
    "cz",
    "趙長鵬",
]


def normalize(text: str) -> str:
    return (text or "").lower()


def load_all_articles():
    articles = []
    for root, _, files in os.walk(BASE_DIR):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for art in data.get("articles", []):
                    art["_src_file"] = fpath
                    articles.append(art)
            except Exception as e:
                print(f"❌ 讀取失敗 {fpath}: {e}")
    print(f"共載入 {len(articles)} 篇 BlockTempo 文章")
    return articles


def search_keywords(articles):
    results = {k: [] for k in KEYWORDS}
    for art in articles:
        title = art.get("title", "")
        content = art.get("content", "")
        combo = normalize(title + "\n" + content)
        for kw in KEYWORDS:
            if kw.lower() in combo:
                results[kw].append(art)
    return results


def save_results(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = {}
    for kw, arts in results.items():
        safe_kw = kw.replace(" ", "_")
        out_path = os.path.join(OUTPUT_DIR, f"BlockTempo_offline_{safe_kw}_{ts}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "site": "BlockTempo",
                    "keyword": kw,
                    "total": len(arts),
                    "articles": arts,
                    "saved_at": datetime.now().isoformat(),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"💾 {kw} → {len(arts)} 篇, 檔案: {out_path}")
        summary[kw] = {
            "total": len(arts),
            "file": out_path,
        }
    return summary


def main():
    articles = load_all_articles()
    results = search_keywords(articles)
    summary = save_results(results)
    print("\n=== 總結 ===")
    for kw, info in summary.items():
        print(f"{kw}: {info['total']} 篇 → {info['file']}")


if __name__ == "__main__":
    main()
