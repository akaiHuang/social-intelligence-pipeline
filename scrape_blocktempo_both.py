#!/usr/bin/env python3
"""Run BlockTempo Exchange (144→1) and BTCtech (105→1)."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from playwright.async_api import async_playwright
from scrape_multi_sites_history import MultiSiteHistoryScraper


async def scrape():
    print("=" * 60)
    print("🗞️  BlockTempo 雙分類爬取")
    print("=" * 60)
    print("1. 交易所分類：144→1 頁")
    print("2. BTCtech 分類：105→1 頁")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        scraper = MultiSiteHistoryScraper()
        scraper.sites_config['blocktempo']['start_page'] = 144
        scraper.sites_config['btctech']['start_page'] = 105

        await scraper.scrape_site(page, 'blocktempo', start_page=144)
        await scraper.scrape_site(page, 'btctech', start_page=105)

        await browser.close()


def main():
    asyncio.run(scrape())


if __name__ == '__main__':
    main()
