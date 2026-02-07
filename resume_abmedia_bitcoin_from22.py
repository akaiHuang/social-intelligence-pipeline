#!/usr/bin/env python3
"""
繼續爬取 ABMedia-比特幣（第 22→1 頁）
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from scrape_multi_sites_history import MultiSiteHistoryScraper
from playwright.async_api import async_playwright

async def main(start):
    print("="*60)
    print(f"🔄 繼續爬取 ABMedia-比特幣（第 {start}→1 頁）")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        scraper = MultiSiteHistoryScraper()

        try:
            await scraper.scrape_site(page, 'abmedia_bitcoin', start_page=start)
            print("\n" + "="*60)
            print("✅ ABMedia-比特幣 爬取完成（或已到起始頁）")
            print("="*60)
        except Exception as e:
            print("❌ 發生錯誤：", e)
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    start = 22
    if len(sys.argv) > 1:
        start = int(sys.argv[1])
    asyncio.run(main(start))
