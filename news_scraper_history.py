"""
加密貨幣新聞爬蟲 - 歷史文章版
透過搜尋和分類頁面爬取歷史文章
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
import re

class HistoryNewsScraper:
    def __init__(self):
        self.keywords = [
            'Bitcoin', '比特幣',
            'BTC',
        ]
        
        self.output_dir = 'output/news_history'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def matches_keywords(self, text):
        """檢查文字是否包含關鍵字"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    async def scrape_blocktempo_category(self, page, max_pages=10):
        """
        爬取動區動趨的分類頁面
        可以翻頁抓取更多歷史文章
        """
        print("\n🔍 正在爬取：動區動趨 - 加密貨幣市場分類")
        print("=" * 60)
        
        base_url = "https://www.blocktempo.com/category/cryptocurrency-market"
        articles = []
        
        for page_num in range(1, max_pages + 1):
            try:
                # 構建分頁 URL
                if page_num == 1:
                    url = base_url
                else:
                    url = f"{base_url}/page/{page_num}"
                
                print(f"\n📄 第 {page_num} 頁: {url}")
                
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(2000)
                
                # 檢查是否還有內容
                article_elements = await page.query_selector_all('article, .post-item, .article-item')
                
                if not article_elements:
                    print(f"⚠️  第 {page_num} 頁沒有找到文章,停止爬取")
                    break
                
                print(f"找到 {len(article_elements)} 篇文章")
                
                for elem in article_elements:
                    try:
                        # 提取標題
                        title_elem = await elem.query_selector('h2, h3, .title, .post-title, a')
                        title = await title_elem.inner_text() if title_elem else ''
                        
                        # 提取連結
                        link_elem = await elem.query_selector('a')
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = f"https://www.blocktempo.com{link}"
                        
                        # 提取摘要
                        summary_elem = await elem.query_selector('.excerpt, .summary, p')
                        summary = await summary_elem.inner_text() if summary_elem else ''
                        
                        # 提取日期 - 優先從 URL 提取
                        year = None
                        date = ''
                        
                        # 方法1: 從 URL 提取 (最可靠)
                        if link:
                            url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
                            if url_match:
                                year = int(url_match.group(1))
                                month = url_match.group(2)
                                day = url_match.group(3)
                                date = f"{year}-{month}-{day}"
                        
                        # 方法2: 從日期元素提取
                        if not year:
                            date_elem = await elem.query_selector('time, .date, .post-date, [datetime]')
                            if date_elem:
                                date = await date_elem.inner_text()
                                # 嘗試從 datetime 屬性取得
                                if not date:
                                    date = await date_elem.get_attribute('datetime')
                                
                                if date:
                                    year_match = re.search(r'20\d{2}', date)
                                    if year_match:
                                        year = int(year_match.group())
                        
                        if title and link:
                            articles.append({
                                'title': title.strip(),
                                'link': link,
                                'summary': summary.strip()[:200],
                                'date': date.strip(),
                                'year': year,
                                'source': 'BlockTempo',
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                            # 顯示年份資訊
                            year_info = f"[{year}]" if year else "[年份未知]"
                            print(f"  ✓ {year_info} {title[:40]}...")
                    
                    except Exception as e:
                        continue
                
                await page.wait_for_timeout(1000)  # 避免請求過快
                
            except Exception as e:
                print(f"❌ 第 {page_num} 頁爬取失敗: {e}")
                break
        
        print(f"\n✅ BlockTempo: 共找到 {len(articles)} 篇文章")
        return articles
    
    async def scrape_abmedia_category(self, page, max_pages=10):
        """
        爬取鏈新聞的比特幣分類
        """
        print("\n🔍 正在爬取：鏈新聞 - 比特幣分類")
        print("=" * 60)
        
        base_url = "https://abmedia.io/category/invsetments/bitcoin"
        articles = []
        
        for page_num in range(1, max_pages + 1):
            try:
                # 構建分頁 URL
                if page_num == 1:
                    url = base_url
                else:
                    url = f"{base_url}/page/{page_num}"
                
                print(f"\n📄 第 {page_num} 頁: {url}")
                
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(2000)
                
                # 檢查是否還有內容
                article_elements = await page.query_selector_all('article, .post, .news-item')
                
                if not article_elements:
                    print(f"⚠️  第 {page_num} 頁沒有找到文章,停止爬取")
                    break
                
                print(f"找到 {len(article_elements)} 篇文章")
                
                for elem in article_elements:
                    try:
                        # 提取標題
                        title_elem = await elem.query_selector('h1, h2, h3, .title, a')
                        title = await title_elem.inner_text() if title_elem else ''
                        
                        # 提取連結
                        link_elem = await elem.query_selector('a')
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = f"https://abmedia.io{link}"
                        
                        # 提取摘要
                        summary_elem = await elem.query_selector('.excerpt, .description, p')
                        summary = await summary_elem.inner_text() if summary_elem else ''
                        
                        # 提取日期 - 優先從 URL 提取
                        year = None
                        date = ''
                        
                        # 方法1: 從 URL 提取 (最可靠)
                        if link:
                            url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
                            if url_match:
                                year = int(url_match.group(1))
                                month = url_match.group(2)
                                day = url_match.group(3)
                                date = f"{year}-{month}-{day}"
                        
                        # 方法2: 從日期元素提取
                        if not year:
                            date_elem = await elem.query_selector('time, .date, .meta, [datetime]')
                            if date_elem:
                                date = await date_elem.inner_text()
                                if not date:
                                    date = await date_elem.get_attribute('datetime')
                                
                                if date:
                                    year_match = re.search(r'20\d{2}', date)
                                    if year_match:
                                        year = int(year_match.group())
                        
                        if title and link:
                            articles.append({
                                'title': title.strip(),
                                'link': link,
                                'summary': summary.strip()[:200],
                                'date': date.strip(),
                                'year': year,
                                'source': 'ABMedia',
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                            year_info = f"[{year}]" if year else "[年份未知]"
                            print(f"  ✓ {year_info} {title[:40]}...")
                    
                    except Exception as e:
                        continue
                
                await page.wait_for_timeout(1000)
                
            except Exception as e:
                print(f"❌ 第 {page_num} 頁爬取失敗: {e}")
                break
        
        print(f"\n✅ ABMedia: 共找到 {len(articles)} 篇文章")
        return articles
    
    async def scrape_blockcast_category(self, page, max_pages=10):
        """
        爬取區塊客的比特幣相關文章
        """
        print("\n🔍 正在爬取：區塊客 - 市場幣價分類")
        print("=" * 60)
        
        base_url = "https://blockcast.it/category/news/market/price"
        articles = []
        
        for page_num in range(1, max_pages + 1):
            try:
                # 構建分頁 URL
                if page_num == 1:
                    url = base_url
                else:
                    url = f"{base_url}/page/{page_num}"
                
                print(f"\n📄 第 {page_num} 頁: {url}")
                
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(2000)
                
                # 檢查是否還有內容
                article_elements = await page.query_selector_all('article, .post-item, .news-item')
                
                if not article_elements:
                    print(f"⚠️  第 {page_num} 頁沒有找到文章,停止爬取")
                    break
                
                print(f"找到 {len(article_elements)} 篇文章")
                
                for elem in article_elements:
                    try:
                        # 提取標題
                        title_elem = await elem.query_selector('h1, h2, h3, .title, a')
                        title = await title_elem.inner_text() if title_elem else ''
                        
                        # 提取連結
                        link_elem = await elem.query_selector('a')
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = f"https://blockcast.it{link}"
                        
                        # 提取摘要
                        summary_elem = await elem.query_selector('.excerpt, p')
                        summary = await summary_elem.inner_text() if summary_elem else ''
                        
                        # 提取日期
                        date_elem = await elem.query_selector('time, .date')
                        date = ''
                        if date_elem:
                            date = await date_elem.inner_text()
                            if not date:
                                date = await date_elem.get_attribute('datetime')
                        
                        # 提取年份
                        year = None
                        if date:
                            year_match = re.search(r'20\d{2}', date)
                            if year_match:
                                year = int(year_match.group())
                        
                        # 只保留比特幣相關文章
                        if title and link and self.matches_keywords(f"{title} {summary}"):
                            articles.append({
                                'title': title.strip(),
                                'link': link,
                                'summary': summary.strip()[:200],
                                'date': date.strip(),
                                'year': year,
                                'source': 'Blockcast',
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                            year_info = f"[{year}]" if year else "[年份未知]"
                            print(f"  ✓ {year_info} {title[:40]}...")
                    
                    except Exception as e:
                        continue
                
                await page.wait_for_timeout(1000)
                
            except Exception as e:
                print(f"❌ 第 {page_num} 頁爬取失敗: {e}")
                break
        
        print(f"\n✅ Blockcast: 共找到 {len(articles)} 篇文章")
        return articles
    
    def save_by_year(self, all_articles):
        """按年份儲存文章"""
        if not all_articles:
            print("\n⚠️  沒有找到文章")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 按年份分類
        by_year = {}
        no_year = []
        
        for article in all_articles:
            year = article.get('year')
            if year:
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(article)
            else:
                no_year.append(article)
        
        # 儲存各年份
        for year in sorted(by_year.keys()):
            articles = by_year[year]
            year_dir = os.path.join(self.output_dir, str(year))
            os.makedirs(year_dir, exist_ok=True)
            
            filename = os.path.join(year_dir, f'bitcoin_news_{timestamp}.json')
            
            output_data = {
                'year': year,
                'total_articles': len(articles),
                'articles': articles,
                'by_source': {},
                'scraped_at': datetime.now().isoformat()
            }
            
            # 統計來源
            for article in articles:
                source = article['source']
                output_data['by_source'][source] = output_data['by_source'].get(source, 0) + 1
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 {year} 年: 已儲存 {len(articles)} 篇文章到 {filename}")
            print(f"   來源分布: {output_data['by_source']}")
        
        # 儲存年份未知的文章
        if no_year:
            unknown_dir = os.path.join(self.output_dir, 'unknown_year')
            os.makedirs(unknown_dir, exist_ok=True)
            filename = os.path.join(unknown_dir, f'bitcoin_news_{timestamp}.json')
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'year': None,
                    'total_articles': len(no_year),
                    'articles': no_year,
                    'scraped_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 年份未知: 已儲存 {len(no_year)} 篇文章")
        
        # 生成總覽
        summary_file = os.path.join(self.output_dir, f'summary_{timestamp}.json')
        summary = {
            'total_articles': len(all_articles),
            'by_year': {str(year): len(articles) for year, articles in by_year.items()},
            'unknown_year': len(no_year),
            'year_range': {
                'earliest': min(by_year.keys()) if by_year else None,
                'latest': max(by_year.keys()) if by_year else None
            },
            'by_source': {},
            'scraped_at': datetime.now().isoformat()
        }
        
        for article in all_articles:
            source = article['source']
            summary['by_source'][source] = summary['by_source'].get(source, 0) + 1
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 總覽統計")
        print("=" * 60)
        print(f"總共: {len(all_articles)} 篇文章")
        print(f"年份範圍: {summary['year_range']['earliest']} - {summary['year_range']['latest']}")
        print(f"各年份文章數: {summary['by_year']}")
        print(f"來源統計: {summary['by_source']}")
        print(f"總覽檔案: {summary_file}")
    
    async def scrape_all(self, max_pages_per_site=10):
        """爬取所有網站的歷史文章"""
        print("=" * 60)
        print("🚀 開始爬取比特幣歷史新聞")
        print("=" * 60)
        print(f"🔑 關鍵字: {', '.join(self.keywords)}")
        print(f"📄 每個網站最多爬取 {max_pages_per_site} 頁")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            all_articles = []
            
            try:
                # 爬取各網站
                articles = await self.scrape_blocktempo_category(page, max_pages_per_site)
                all_articles.extend(articles)
                
                articles = await self.scrape_abmedia_category(page, max_pages_per_site)
                all_articles.extend(articles)
                
                articles = await self.scrape_blockcast_category(page, max_pages_per_site)
                all_articles.extend(articles)
                
            except Exception as e:
                print(f"\n❌ 爬取過程發生錯誤: {e}")
            
            finally:
                await browser.close()
            
            # 按年份儲存
            self.save_by_year(all_articles)
            
            print("\n" + "=" * 60)
            print("✅ 爬取完成!")
            print("=" * 60)


async def main():
    print("比特幣歷史新聞爬蟲")
    print()
    
    # 輸入要爬取的頁數
    try:
        max_pages = int(input("每個網站要爬取幾頁? (建議 5-20 頁，預設 10): ") or "10")
    except ValueError:
        max_pages = 10
    
    print()
    scraper = HistoryNewsScraper()
    await scraper.scrape_all(max_pages_per_site=max_pages)


if __name__ == "__main__":
    asyncio.run(main())
