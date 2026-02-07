#!/usr/bin/env python3
"""
繼續爬取 Blockcast 剩餘頁面
從第 833 頁爬到第 1 頁
"""

import asyncio
import sys
import os

# 確保可以導入主程式
sys.path.insert(0, os.path.dirname(__file__))

from scrape_multi_sites_history import MultiSiteHistoryScraper
from playwright.async_api import async_playwright

async def main():
    """繼續爬取 Blockcast"""
    
    print("=" * 60)
    print("🔄 繼續爬取 Blockcast")
    print("=" * 60)
    print("起始頁: 第 833 頁")
    print("結束頁: 第 1 頁")
    print("已完成: 第 1235 → 834 頁 (4,016 篇)")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        scraper = MultiSiteHistoryScraper()
        
        try:
            # 只爬 Blockcast，從第 833 頁開始
            await scraper.scrape_site(page, 'blockcast', start_page=833)
            
            print("\n" + "=" * 60)
            print("✅ Blockcast 繼續爬取完成！")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n⚠️  使用者中斷")
        except Exception as e:
            print(f"\n❌ 錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
