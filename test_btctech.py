"""
測試 BTCtech (Bitcoin 技術分類) 爬取
"""
import asyncio
from scrape_multi_sites_history import MultiSiteHistoryScraper

async def test():
    scraper = MultiSiteHistoryScraper()
    # 只測試 BTCtech，爬最後 2 頁
    await scraper.scrape_all_sites(sites=['btctech'], num_pages=2)

if __name__ == '__main__':
    asyncio.run(test())
