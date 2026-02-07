#!/usr/bin/env python3
"""
測試 ABMedia 市場分類
確認正確的 URL 並測試爬取
"""

import asyncio
from playwright.async_api import async_playwright

async def test_abmedia():
    """測試 ABMedia 市場分類"""
    
    # 測試兩個可能的 URL
    test_urls = [
        ('investments (正確拼寫)', 'https://abmedia.io/category/investments/market/page/182'),
        ('invsetments (錯誤拼寫)', 'https://abmedia.io/category/invsetments/market/page/182'),
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("=" * 60)
        print("🧪 測試 ABMedia 市場分類 URL")
        print("=" * 60)
        
        for name, url in test_urls:
            print(f"\n📝 測試 {name}")
            print(f"🔗 URL: {url}")
            
            try:
                response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                print(f"✅ 狀態碼: {response.status}")
                
                if response.status == 200:
                    await page.wait_for_timeout(2000)
                    
                    # 檢查文章
                    articles = await page.query_selector_all('article, .post')
                    print(f"✅ 找到 {len(articles)} 篇文章")
                    
                    if articles:
                        # 測試第一篇文章
                        first_article = articles[0]
                        title_elem = await first_article.query_selector('h2 a, h3 a, .entry-title a')
                        if title_elem:
                            title = await title_elem.inner_text()
                            link = await title_elem.get_attribute('href')
                            print(f"📰 第一篇: {title[:50]}...")
                            print(f"🔗 連結: {link}")
                        
                        print(f"✅ 此 URL 可用！")
                    else:
                        print(f"⚠️  未找到文章元素")
                else:
                    print(f"❌ HTTP {response.status}")
                    
            except Exception as e:
                print(f"❌ 錯誤: {e}")
        
        await browser.close()
        
        print("\n" + "=" * 60)
        print("測試完成")
        print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_abmedia())
