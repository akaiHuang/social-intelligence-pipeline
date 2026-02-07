"""
測試 BlockTempo 日期抓取
檢查文章詳細頁面的日期欄位
"""
import asyncio
from playwright.async_api import async_playwright

async def test_blocktempo_date():
    """測試 BlockTempo 文章的日期抓取"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 顯示瀏覽器方便觀察
        page = await browser.new_page()
        
        # 測試：抓取第 552 頁（最後一頁）的第一篇文章
        print("=" * 60)
        print("測試 BlockTempo 日期抓取")
        print("=" * 60)
        
        list_url = "https://www.blocktempo.com/category/cryptocurrency-market/page/552/"
        print(f"\n📄 前往列表頁: {list_url}")
        
        await page.goto(list_url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(2000)
        
        # 找第一篇文章
        article_elements = await page.query_selector_all('article, .post, .article-item')
        print(f"✓ 找到 {len(article_elements)} 篇文章")
        
        if article_elements:
            first_article = article_elements[0]
            
            # 抓取標題和連結
            link_elem = await first_article.query_selector('h2 a, h3 a, .entry-title a')
            if link_elem:
                title = await link_elem.inner_text()
                link = await link_elem.get_attribute('href')
                
                print(f"\n📰 第一篇文章:")
                print(f"   標題: {title}")
                print(f"   連結: {link}")
                
                # 進入文章詳細頁面
                print(f"\n🔗 進入文章頁面...")
                await page.goto(link, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)
                
                print("\n" + "=" * 60)
                print("開始測試各種日期選擇器")
                print("=" * 60)
                
                # 測試多種日期選擇器
                date_selectors = [
                    'time',
                    '.entry-date',
                    '.post-date',
                    '.published',
                    '.date',
                    'time[datetime]',
                    '.entry-meta time',
                    'meta[property="article:published_time"]',
                    '.td-post-date',
                    '.updated',
                    'span.date',
                    'div.date'
                ]
                
                found_dates = []
                
                for selector in date_selectors:
                    try:
                        if selector == 'meta[property="article:published_time"]':
                            # Meta 標籤用 get_attribute
                            meta_elem = await page.query_selector(selector)
                            if meta_elem:
                                date_value = await meta_elem.get_attribute('content')
                                if date_value:
                                    print(f"✓ [{selector}] = {date_value}")
                                    found_dates.append((selector, date_value))
                        else:
                            # 其他用 inner_text
                            date_elem = await page.query_selector(selector)
                            if date_elem:
                                date_text = await date_elem.inner_text()
                                if date_text:
                                    print(f"✓ [{selector}] = {date_text.strip()}")
                                    found_dates.append((selector, date_text.strip()))
                                    
                                # 如果有 datetime 屬性也顯示
                                datetime_attr = await date_elem.get_attribute('datetime')
                                if datetime_attr:
                                    print(f"   └─ datetime 屬性: {datetime_attr}")
                    except Exception as e:
                        pass
                
                print("\n" + "=" * 60)
                print(f"總共找到 {len(found_dates)} 個日期欄位")
                print("=" * 60)
                
                if found_dates:
                    print("\n✅ 找到的日期資訊:")
                    for selector, date_value in found_dates:
                        print(f"   • {selector}: {date_value}")
                else:
                    print("\n❌ 沒有找到任何日期資訊！")
                    print("\n🔍 讓我抓取整個頁面的 HTML 片段看看...")
                    
                    # 抓取文章 meta 區域
                    meta_selectors = [
                        '.entry-meta',
                        '.post-meta',
                        '.article-meta',
                        'header.entry-header',
                        '.td-post-header'
                    ]
                    
                    for meta_sel in meta_selectors:
                        meta_elem = await page.query_selector(meta_sel)
                        if meta_elem:
                            meta_html = await meta_elem.inner_html()
                            print(f"\n📋 [{meta_sel}] HTML:")
                            print(meta_html[:500])  # 只顯示前 500 字元
                            break
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_blocktempo_date())
