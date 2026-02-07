"""
加密貨幣新聞爬蟲
支援多個台灣主流區塊鏈新聞網站
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
import re

class NewsScraper:
    def __init__(self):
        self.keywords = [
            'BTC', 'Bitcoin', '比特幣', '比特币',
            'Elon Musk', 'Elon', 'Musk', '馬斯克', '马斯克',
            'Trump', '川普', '特朗普',
            'Michael Saylor', 'Saylor',
            'CZ', '趙長鵬',
        ]
        
        self.output_dir = 'output/news'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def matches_keywords(self, text):
        """檢查文字是否包含關鍵字"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    async def scrape_blocktempo(self, page, max_articles=50):
        """
        爬取動區動趨 BlockTempo
        URL: https://www.blocktempo.com
        """
        print("\n🔍 正在爬取：動區動趨 (BlockTempo)")
        print("=" * 60)
        
        url = "https://www.blocktempo.com"
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(3000)
        
        articles = []
        
        # 爬取文章列表
        article_elements = await page.query_selector_all('article, .post-item, .article-item')
        
        print(f"📄 找到 {len(article_elements)} 個文章元素")
        
        for elem in article_elements[:max_articles]:
            try:
                # 提取標題
                title_elem = await elem.query_selector('h2, h3, .title, .post-title')
                title = await title_elem.inner_text() if title_elem else ''
                
                # 提取連結
                link_elem = await elem.query_selector('a')
                link = await link_elem.get_attribute('href') if link_elem else ''
                if link and not link.startswith('http'):
                    link = f"{url}{link}"
                
                # 提取摘要
                summary_elem = await elem.query_selector('.excerpt, .summary, p')
                summary = await summary_elem.inner_text() if summary_elem else ''
                
                # 提取日期
                date_elem = await elem.query_selector('time, .date, .post-date')
                date = await date_elem.inner_text() if date_elem else ''
                
                # 檢查是否匹配關鍵字
                if title and (self.matches_keywords(title) or self.matches_keywords(summary)):
                    articles.append({
                        'title': title.strip(),
                        'link': link,
                        'summary': summary.strip()[:200],
                        'date': date.strip(),
                        'source': 'BlockTempo',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}...")
                
            except Exception as e:
                continue
        
        print(f"\n✅ BlockTempo: 找到 {len(articles)} 篇相關文章")
        return articles
    
    async def scrape_abmedia(self, page, max_articles=50):
        """
        爬取鏈新聞 ABMedia
        URL: https://abmedia.io
        """
        print("\n🔍 正在爬取：鏈新聞 (ABMedia)")
        print("=" * 60)
        
        url = "https://abmedia.io"
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(3000)
        
        articles = []
        
        # 爬取文章列表
        article_elements = await page.query_selector_all('article, .post, .news-item')
        
        print(f"📄 找到 {len(article_elements)} 個文章元素")
        
        for elem in article_elements[:max_articles]:
            try:
                # 提取標題
                title_elem = await elem.query_selector('h1, h2, h3, .title')
                title = await title_elem.inner_text() if title_elem else ''
                
                # 提取連結
                link_elem = await elem.query_selector('a')
                link = await link_elem.get_attribute('href') if link_elem else ''
                if link and not link.startswith('http'):
                    link = f"{url}{link}"
                
                # 提取摘要
                summary_elem = await elem.query_selector('.excerpt, .description, p')
                summary = await summary_elem.inner_text() if summary_elem else ''
                
                # 提取日期
                date_elem = await elem.query_selector('time, .date')
                date = await date_elem.inner_text() if date_elem else ''
                
                # 檢查是否匹配關鍵字
                if title and (self.matches_keywords(title) or self.matches_keywords(summary)):
                    articles.append({
                        'title': title.strip(),
                        'link': link,
                        'summary': summary.strip()[:200],
                        'date': date.strip(),
                        'source': 'ABMedia',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}...")
                
            except Exception as e:
                continue
        
        print(f"\n✅ ABMedia: 找到 {len(articles)} 篇相關文章")
        return articles
    
    async def scrape_blockcast(self, page, max_articles=50):
        """
        爬取區塊客 Blockcast
        URL: https://blockcast.it
        """
        print("\n🔍 正在爬取：區塊客 (Blockcast)")
        print("=" * 60)
        
        url = "https://blockcast.it"
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(3000)
        
        articles = []
        
        # 爬取文章列表
        article_elements = await page.query_selector_all('article, .post-item')
        
        print(f"📄 找到 {len(article_elements)} 個文章元素")
        
        for elem in article_elements[:max_articles]:
            try:
                # 提取標題
                title_elem = await elem.query_selector('h1, h2, h3, .title')
                title = await title_elem.inner_text() if title_elem else ''
                
                # 提取連結
                link_elem = await elem.query_selector('a')
                link = await link_elem.get_attribute('href') if link_elem else ''
                if link and not link.startswith('http'):
                    link = f"{url}{link}"
                
                # 提取摘要
                summary_elem = await elem.query_selector('.excerpt, p')
                summary = await summary_elem.inner_text() if summary_elem else ''
                
                # 提取日期
                date_elem = await elem.query_selector('time, .date')
                date = await date_elem.inner_text() if date_elem else ''
                
                # 檢查是否匹配關鍵字
                if title and (self.matches_keywords(title) or self.matches_keywords(summary)):
                    articles.append({
                        'title': title.strip(),
                        'link': link,
                        'summary': summary.strip()[:200],
                        'date': date.strip(),
                        'source': 'Blockcast',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}...")
                
            except Exception as e:
                continue
        
        print(f"\n✅ Blockcast: 找到 {len(articles)} 篇相關文章")
        return articles
    
    async def scrape_cnyes(self, page, max_articles=50):
        """
        爬取鉅亨網區塊鏈
        URL: https://news.cnyes.com/news/cat/bc
        """
        print("\n🔍 正在爬取：鉅亨網區塊鏈 (Cnyes)")
        print("=" * 60)
        
        url = "https://news.cnyes.com/news/cat/bc"
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(3000)
        
        articles = []
        
        # 爬取文章列表
        article_elements = await page.query_selector_all('article, .news-item, ._1m83')
        
        print(f"📄 找到 {len(article_elements)} 個文章元素")
        
        for elem in article_elements[:max_articles]:
            try:
                # 提取標題
                title_elem = await elem.query_selector('h3, h2, a')
                title = await title_elem.inner_text() if title_elem else ''
                
                # 提取連結
                link_elem = await elem.query_selector('a')
                link = await link_elem.get_attribute('href') if link_elem else ''
                if link and not link.startswith('http'):
                    link = f"https://news.cnyes.com{link}"
                
                # 提取摘要
                summary_elem = await elem.query_selector('p, .summary')
                summary = await summary_elem.inner_text() if summary_elem else ''
                
                # 提取日期
                date_elem = await elem.query_selector('time, .date, ._2jPO')
                date = await date_elem.inner_text() if date_elem else ''
                
                # 檢查是否匹配關鍵字
                if title and (self.matches_keywords(title) or self.matches_keywords(summary)):
                    articles.append({
                        'title': title.strip(),
                        'link': link,
                        'summary': summary.strip()[:200],
                        'date': date.strip(),
                        'source': 'Cnyes',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}...")
                
            except Exception as e:
                continue
        
        print(f"\n✅ Cnyes: 找到 {len(articles)} 篇相關文章")
        return articles
    
    def categorize_article(self, article):
        """根據內容分類文章"""
        title = article['title'].lower()
        summary = article['summary'].lower()
        content = f"{title} {summary}"
        
        # BTC 相關
        if any(k in content for k in ['btc', 'bitcoin', '比特幣', '比特币']):
            return 'bitcoin'
        
        # Elon Musk 相關
        if any(k in content for k in ['elon', 'musk', '馬斯克', '马斯克']):
            return 'elon_musk'
        
        # Trump 相關
        if any(k in content for k in ['trump', '川普', '特朗普']):
            return 'trump'
        
        # Michael Saylor 相關
        if any(k in content for k in ['saylor', 'microstrategy']):
            return 'saylor'
        
        # CZ 相關
        if any(k in content for k in ['cz', '趙長鵬', 'binance', '幣安']):
            return 'cz'
        
        return 'other'
    
    def save_articles(self, all_articles):
        """儲存文章並按類別分類"""
        if not all_articles:
            print("\n⚠️  沒有找到相關文章")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 按類別分類
        categorized = {}
        for article in all_articles:
            category = self.categorize_article(article)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)
        
        # 儲存各類別
        for category, articles in categorized.items():
            category_dir = os.path.join(self.output_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            filename = os.path.join(category_dir, f'news_{timestamp}.json')
            
            output_data = {
                'category': category,
                'total_articles': len(articles),
                'articles': articles,
                'keywords': self.keywords,
                'scraped_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 {category}: 已儲存 {len(articles)} 篇文章到 {filename}")
        
        # 儲存總覽
        summary_file = os.path.join(self.output_dir, f'summary_{timestamp}.json')
        summary = {
            'total_articles': len(all_articles),
            'by_category': {cat: len(arts) for cat, arts in categorized.items()},
            'by_source': {},
            'scraped_at': datetime.now().isoformat()
        }
        
        # 統計來源
        for article in all_articles:
            source = article['source']
            summary['by_source'][source] = summary['by_source'].get(source, 0) + 1
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 總覽: {summary_file}")
        print(f"總共 {len(all_articles)} 篇文章")
        print(f"分類統計: {summary['by_category']}")
        print(f"來源統計: {summary['by_source']}")
    
    async def scrape_all(self):
        """爬取所有網站"""
        print("=" * 60)
        print("🚀 開始爬取加密貨幣新聞")
        print("=" * 60)
        print(f"🔑 關鍵字: {', '.join(self.keywords)}")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            all_articles = []
            
            try:
                # 爬取各網站
                articles = await self.scrape_blocktempo(page)
                all_articles.extend(articles)
                
                articles = await self.scrape_abmedia(page)
                all_articles.extend(articles)
                
                articles = await self.scrape_blockcast(page)
                all_articles.extend(articles)
                
                articles = await self.scrape_cnyes(page)
                all_articles.extend(articles)
                
            except Exception as e:
                print(f"\n❌ 爬取過程發生錯誤: {e}")
            
            finally:
                await browser.close()
            
            # 儲存結果
            self.save_articles(all_articles)
            
            print("\n" + "=" * 60)
            print("✅ 爬取完成!")
            print("=" * 60)


async def main():
    scraper = NewsScraper()
    await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())
