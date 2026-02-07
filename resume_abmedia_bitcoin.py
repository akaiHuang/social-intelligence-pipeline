#!/usr/bin/env python3
"""
繼續爬取 ABMedia-比特幣 未完成頁面
從第 45 頁爬到第 1 頁
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from scrape_multi_sites_history import MultiSiteHistoryScraper
from playwright.async_api import async_playwright

async def main():
    print("="*60)
    print("🔄 繼續爬取 ABMedia-比特幣（第 45→1 頁）")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        scraper = MultiSiteHistoryScraper()

        # 從第 45 頁開始（目前最小頁為 46）
        start = 45
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
    asyncio.run(main())
