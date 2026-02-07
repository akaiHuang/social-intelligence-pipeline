"""
測試 Blockcast 爬取
"""
import asyncio
from scrape_multi_sites_history import MultiSiteHistoryScraper

async def test():
    scraper = MultiSiteHistoryScraper()
    # 只測試 Blockcast，爬前 2 頁（第1頁和第2頁）
    await scraper.scrape_all_sites(sites=['blockcast'], num_pages=2)

if __name__ == '__main__':
    asyncio.run(test())
