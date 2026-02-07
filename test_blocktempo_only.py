"""
測試 BlockTempo 單獨爬取
確認日期抓取是否正常
"""
import asyncio
from scrape_multi_sites_history import MultiSiteHistoryScraper

async def test():
    scraper = MultiSiteHistoryScraper()
    # 只測試 BlockTempo，爬最後 2 頁
    await scraper.scrape_all_sites(sites=['blocktempo'], num_pages=2)

if __name__ == '__main__':
    asyncio.run(test())
