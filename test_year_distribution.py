#!/usr/bin/env python3
"""
測試 Blockcast 不同頁碼區間的年份分布
目標: 找出 2018-2024 年文章所在的頁碼範圍
"""
import asyncio
from scrape_blockcast_history import BlockcastHistoryScraper

async def test_page_ranges():
    """測試多個頁碼區間,快速找出年份分布"""
    scraper = BlockcastHistoryScraper()
    
    # 測試策略: 每 100 頁抓 5 頁樣本
    test_ranges = [
        (1400, 5),  # 最新區間 (預期 2025)
        (1300, 5),  # 
        (1200, 5),  # 
        (1100, 5),  # 
        (1000, 5),  # 
        (900, 5),   # 
        (800, 5),   # 
        (700, 5),   # 
        (600, 5),   # 
        (500, 5),   # 
    ]
    
    print("🔍 開始測試不同頁碼區間的年份分布...")
    print("=" * 80)
    
    for start_page, num_pages in test_ranges:
        print(f"\n📄 測試頁碼 {start_page} - {start_page-num_pages+1}")
        await scraper.scrape(start_page=start_page, num_pages=num_pages)
        print("-" * 80)
        await asyncio.sleep(2)  # 短暫休息

if __name__ == "__main__":
    asyncio.run(test_page_ranges())
