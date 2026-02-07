import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

SEARCH_CONFIGS = [
    # ABMedia 搜尋
    {
        "site": "ABMedia",
        "keyword": "elon musk",
        "start_page": 36,
        "end_page": 1,
        "base_url": "https://abmedia.io/page/{page}?s=elon+musk",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
    {
        "site": "ABMedia",
        "keyword": "trump",
        "start_page": 61,
        "end_page": 1,
        "base_url": "https://abmedia.io/page/{page}?s=trump",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
    {
        "site": "ABMedia",
        "keyword": "cz",
        "start_page": 54,
        "end_page": 1,
        "base_url": "https://abmedia.io/page/{page}?s=cz",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
    # BlockTempo 搜尋
    {
        "site": "BlockTempo",
        "keyword": "elon musk",
        "start_page": 56,
        "end_page": 1,
        "base_url": "https://www.blocktempo.com/page/{page}/?s=elon+musk",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
    {
        "site": "BlockTempo",
        "keyword": "trump",
        "start_page": 27,
        "end_page": 1,
        "base_url": "https://www.blocktempo.com/page/{page}/?s=trump",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
    {
        "site": "BlockTempo",
        "keyword": "trump",
        "start_page": 26,
        "end_page": 1,
        "base_url": "https://www.blocktempo.com/page/{page}/?s=trump",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
    {
        "site": "BlockTempo",
        "keyword": "cz",
        "start_page": 104,
        "end_page": 1,
        "base_url": "https://www.blocktempo.com/page/{page}/?s=cz",
        "article_selector": "article, .post, .article-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
    },
]

OUTPUT_DIR = "output/keyword_search"
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def scrape_search(config, page):
    site = config["site"]
    keyword = config["keyword"]
    start = config["start_page"]
    end = config["end_page"]
    article_sel = config["article_selector"]
    title_sel = config["title_selector"]

    articles = []

    print(f"\n==== {site} | {keyword} | {start}→{end} ====")

    for p in range(start, end - 1, -1):
        url = config["base_url"].format(page=p)
        print(f"📄 page {p}: {url}")
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if not resp or resp.status != 200:
                print(f"  ❌ HTTP {resp.status if resp else 'no response'}，跳過這頁")
                continue
            await page.wait_for_timeout(1500)

            elems = await page.query_selector_all(article_sel)
            print(f"  找到 {len(elems)} 篇")

            for idx, art in enumerate(elems, start=1):
                try:
                    title_elem = await art.query_selector(title_sel)
                    if not title_elem:
                        continue
                    title = (await title_elem.inner_text()).strip()
                    link = await title_elem.get_attribute("href")
                    if not link:
                        continue
                    print(f"   {p}-{idx}: {title[:60]}")
                    articles.append({
                        "site": site,
                        "keyword": keyword,
                        "page": p,
                        "title": title,
                        "link": link,
                    })
                except Exception as e:
                    print(f"   ❌ 解析文章失敗: {e}")
                    continue
        except Exception as e:
            print(f"  ❌ 抓取頁面失敗: {e}")
            continue

    # 儲存結果
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_kw = keyword.replace(" ", "_")
    out_path = os.path.join(OUTPUT_DIR, f"{site}_{safe_kw}_{start}_to_{end}_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "site": site,
            "keyword": keyword,
            "start_page": start,
            "end_page": end,
            "total": len(articles),
            "articles": articles,
            "saved_at": datetime.now().isoformat(),
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 已儲存 {len(articles)} 篇到 {out_path}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for cfg in SEARCH_CONFIGS:
            await scrape_search(cfg, page)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
