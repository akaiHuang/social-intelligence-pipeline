#!/usr/bin/env python3
"""
爬取 ABMedia 市場分類
從第 182 頁爬到第 1 頁
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from scrape_multi_sites_history import MultiSiteHistoryScraper
from playwright.async_api import async_playwright

async def main():
    """爬取 ABMedia 市場分類"""
    
    print("=" * 60)
    print("🗞️  爬取 ABMedia 市場分類")
    print("=" * 60)
    print("起始頁: 第 182 頁")
    print("結束頁: 第 1 頁")
    print("目標: 182 頁文章")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        scraper = MultiSiteHistoryScraper()
        
        # 臨時修改 ABMedia 市場的起始頁為 182
        scraper.sites_config['abmedia_market']['start_page'] = 182
        
        try:
            # 只爬 ABMedia 市場分類，從第 182 頁開始
            await scraper.scrape_site(page, 'abmedia_market', start_page=182)
            
            print("\n" + "=" * 60)
            print("✅ ABMedia 市場分類爬取完成！")
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
