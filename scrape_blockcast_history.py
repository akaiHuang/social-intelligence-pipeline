"""
區塊客歷史新聞爬蟲 - 從舊到新
從第 1235 頁開始往前爬取 (2018-2019 年的文章)
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
import re

class BlockcastHistoryScraper:
    def __init__(self):
        self.output_dir = 'output/news_history'
        os.makedirs(self.output_dir, exist_ok=True)
        # 要過濾的重複文章（每頁都會出現的置頂文章）
        self.skip_urls = [
            'https://blockcast.it/2025/11/14/ethereum-interoperability-the-final-mile-to-mass-adoption/'
        ]
        # 批次儲存設定
        self.batch_size = 30  # 每 30 篇寫入一次
        self.current_batch = []  # 當前批次的文章
        self.total_saved = 0  # 已儲存的文章總數
    
    def _save_batch(self, force=False):
        """
        儲存當前批次的文章
        
        Args:
            force: 是否強制儲存（即使未達到批次大小）
        """
        if not self.current_batch:
            return
        
        if not force and len(self.current_batch) < self.batch_size:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 按年份分類
        by_year = {}
        for article in self.current_batch:
            year = article.get('year')
            if year:
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(article)
        
        # 儲存各年份
        for year in sorted(by_year.keys()):
            articles = by_year[year]
            year_dir = os.path.join(self.output_dir, str(year))
            os.makedirs(year_dir, exist_ok=True)
            
            # 使用 append 模式累加文章
            filename = os.path.join(year_dir, f'blockcast_batch_{timestamp}.json')
            
            output_data = {
                'year': year,
                'batch_articles': len(articles),
                'articles': articles,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 [{year}] 已儲存 {len(articles)} 篇 → {filename}")
        
        self.total_saved += len(self.current_batch)
        print(f"✅ 累計已儲存: {self.total_saved} 篇文章\n")
        
        # 清空當前批次
        self.current_batch = []
    
    async def _fetch_article_content(self, page, article_url):
        """
        進入文章詳細頁面，抓取完整內文和年份
        
        Args:
            page: Playwright page 物件
            article_url: 文章網址
            
        Returns:
            dict: 包含完整內文、發布日期等資訊
        """
        try:
            print(f"    🔗 進入文章: {article_url[:80]}")
            await page.goto(article_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(1500)
            
            # 抓取文章內文 - 嘗試多種選擇器
            content = ''
            content_selectors = [
                '.entry-content',
                'article .entry-content',
                '.post-content',
                '.article-content',
                '.content',
                'main article'
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = await page.query_selector(selector)
                    if content_elem:
                        content = await content_elem.inner_text()
                        if content and len(content) > 100:  # 確保抓到實質內容
                            print(f"    ✓ 使用選擇器 '{selector}' 抓到內文")
                            break
                except:
                    continue
            
            # 如果沒找到完整內容，嘗試抓取所有段落
            if not content or len(content) < 100:
                print(f"    ⚠️  嘗試用段落方式抓取...")
                paragraphs = await page.query_selector_all('article p, .entry-content p, .post-content p')
                content_parts = []
                for p in paragraphs:
                    try:
                        text = await p.inner_text()
                        if text and len(text) > 20:  # 過濾掉太短的段落
                            content_parts.append(text.strip())
                    except:
                        continue
                content = '\n\n'.join(content_parts)
            
            # 再次從 URL 確認年份（最可靠）
            year = None
            date = ''
            url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', article_url)
            if url_match:
                year = int(url_match.group(1))
                month = url_match.group(2)
                day = url_match.group(3)
                date = f"{year}-{month}-{day}"
            
            return {
                'content': content.strip(),
                'year': year,
                'date': date
            }
            
        except Exception as e:
            print(f"    ❌ 抓取文章內容失敗: {e}")
            return {
                'content': '',
                'year': None,
                'date': ''
            }
    
    async def scrape_blockcast_pages(self, page, start_page=1235, num_pages=50):
        """
        從指定頁面開始爬取區塊客文章
        
        Args:
            page: Playwright page 物件
            start_page: 起始頁碼 (預設 1, 最新文章)
            num_pages: 要爬取的頁數 (預設 1235, 涵蓋所有歷史)
        """
        print("\n🔍 正在爬取：區塊客歷史文章")
        print("=" * 60)
        print(f"起始頁: 第 {start_page} 頁")
        print(f"目標: 爬取 {num_pages} 頁")
        print(f"範圍: 頁碼 {start_page} → {start_page + num_pages - 1}")
        print("=" * 60)
        
        all_articles = []
        
        for page_num in range(start_page, start_page + num_pages):  # 從頁碼 1 開始往後
            if page_num > 1235:  # 最多到 1235 頁
                break
            
            try:
                url = f"https://blockcast.it/category/news/page/{page_num}/"
                
                print(f"\n📄 第 {page_num} 頁: {url}")
                
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(2000)
                
                # 爬取文章列表 - 使用更廣泛的選擇器
                article_elements = await page.query_selector_all('article')
                
                if not article_elements:
                    print(f"⚠️  第 {page_num} 頁沒有找到文章")
                    continue
                
                print(f"找到 {len(article_elements)} 篇文章")
                
                # 🔥 修正: 先收集所有文章的基本資訊（標題、連結），再逐一進入文章頁面
                article_links = []
                
                for elem in article_elements:
                    try:
                        # 提取標題和連結
                        title = ''
                        link = ''
                        
                        # 先找到主要連結
                        link_elem = await elem.query_selector('a[rel="bookmark"], h3 a, h2 a, a')
                        if link_elem:
                            link = await link_elem.get_attribute('href')
                            title = await link_elem.inner_text()
                        
                        # 如果沒找到,再試其他方法
                        if not title:
                            title_elem = await elem.query_selector('h1, h2, h3, h4, .title')
                            title = await title_elem.inner_text() if title_elem else ''
                        
                        if link and not link.startswith('http'):
                            link = f"https://blockcast.it{link}"
                        
                        # 🔥 過濾掉置頂重複文章
                        if link in self.skip_urls:
                            continue
                        
                        # 提取摘要
                        summary_elem = await elem.query_selector('.excerpt, .summary, p')
                        summary = await summary_elem.inner_text() if summary_elem else ''
                        
                        if title and link:
                            article_links.append({
                                'title': title.strip(),
                                'link': link,
                                'summary': summary.strip()[:200]
                            })
                    
                    except Exception as e:
                        print(f"  ⚠️  收集文章資訊時出錯: {str(e)[:50]}")
                        continue
                
                print(f"成功收集 {len(article_links)} 篇文章連結")
                
                # 🔥 現在逐一進入文章頁面抓取完整內容
                page_articles = []
                for idx, article_info in enumerate(article_links, 1):
                    try:
                        print(f"\n  [{idx}/{len(article_links)}] {article_info['title'][:50]}...")
                        
                        # 進入文章詳細頁面抓取完整內容
                        article_details = await self._fetch_article_content(page, article_info['link'])
                        
                        # 從 URL 提取年份
                        year = None
                        date = ''
                        url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', article_info['link'])
                        if url_match:
                            year = int(url_match.group(1))
                            month = url_match.group(2)
                            day = url_match.group(3)
                            date = f"{year}-{month}-{day}"
                        
                        # 優先使用文章頁面的年份（更準確）
                        final_year = article_details['year'] if article_details['year'] else year
                        final_date = article_details['date'] if article_details['date'] else date
                        
                        article_data = {
                            'title': article_info['title'],
                            'link': article_info['link'],
                            'summary': article_info['summary'],
                            'content': article_details['content'],  # 完整內文
                            'date': final_date.strip(),
                            'year': final_year,
                            'source': 'Blockcast',
                            'page_num': page_num,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        page_articles.append(article_data)
                        all_articles.append(article_data)
                        
                        # 🔥 立即加入批次，並檢查是否需要儲存
                        self.current_batch.append(article_data)
                        
                        # 顯示年份資訊和內文長度
                        year_info = f"[{final_year}]" if final_year else "[?]"
                        content_len = len(article_details['content'])
                        print(f"  ✓ {year_info} 抓取成功 (內文: {content_len} 字元)")
                        
                        # 🔥 達到批次大小時自動儲存
                        if len(self.current_batch) >= self.batch_size:
                            print(f"\n{'='*60}")
                            print(f"📦 已累積 {len(self.current_batch)} 篇文章，開始批次儲存...")
                            print(f"{'='*60}")
                            self._save_batch()
                    
                    except Exception as e:
                        print(f"  ❌ 錯誤: {str(e)[:100]}")
                        continue
                
                print(f"本頁成功抓取: {len(page_articles)} 篇")
                
                # 每爬 5 頁休息一下
                if (start_page - page_num + 1) % 5 == 0:
                    print("⏸️  休息 3 秒...")
                    await page.wait_for_timeout(3000)
                else:
                    await page.wait_for_timeout(1000)
                
            except Exception as e:
                print(f"❌ 第 {page_num} 頁爬取失敗: {e}")
                continue
        
        # 🔥 爬取完成後，強制儲存剩餘的文章
        if self.current_batch:
            print(f"\n{'='*60}")
            print(f"📦 爬取完成！儲存剩餘 {len(self.current_batch)} 篇文章...")
            print(f"{'='*60}")
            self._save_batch(force=True)
        
        print(f"\n✅ 共成功抓取: {len(all_articles)} 篇文章")
        print(f"💾 總共儲存: {self.total_saved} 篇文章")
        return all_articles
    
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
            
            filename = os.path.join(year_dir, f'blockcast_{timestamp}.json')
            
            output_data = {
                'year': year,
                'total_articles': len(articles),
                'articles': articles,
                'scraped_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 {year} 年: 已儲存 {len(articles)} 篇文章")
            print(f"   檔案: {filename}")
        
        # 儲存年份未知的文章
        if no_year:
            unknown_dir = os.path.join(self.output_dir, 'unknown_year')
            os.makedirs(unknown_dir, exist_ok=True)
            filename = os.path.join(unknown_dir, f'blockcast_{timestamp}.json')
            
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
            'scraped_at': datetime.now().isoformat()
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 總覽統計")
        print("=" * 60)
        print(f"總共: {len(all_articles)} 篇文章")
        if summary['year_range']['earliest']:
            print(f"年份範圍: {summary['year_range']['earliest']} - {summary['year_range']['latest']}")
        print(f"各年份文章數:")
        for year in sorted(by_year.keys()):
            print(f"  {year}: {len(by_year[year])} 篇")
        print(f"\n總覽檔案: {summary_file}")
    
    async def scrape(self, start_page=1235, num_pages=50):
        """執行爬取"""
        print("=" * 60)
        print("🚀 開始爬取區塊客歷史新聞")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            all_articles = []
            
            try:
                articles = await self.scrape_blockcast_pages(page, start_page, num_pages)
                all_articles.extend(articles)
                
            except Exception as e:
                print(f"\n❌ 爬取過程發生錯誤: {e}")
            
            finally:
                await browser.close()
            
            # 🔥 不需要再次儲存，因為已經動態儲存過了
            # 只生成統計摘要
            if all_articles:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                summary_file = os.path.join(self.output_dir, f'summary_{timestamp}.json')
                
                by_year = {}
                for article in all_articles:
                    year = article.get('year')
                    if year:
                        if year not in by_year:
                            by_year[year] = []
                        by_year[year].append(article)
                
                summary = {
                    'total_articles': len(all_articles),
                    'by_year': {year: len(articles) for year, articles in by_year.items()},
                    'year_range': {
                        'earliest': min(by_year.keys()) if by_year else None,
                        'latest': max(by_year.keys()) if by_year else None
                    },
                    'total_saved': self.total_saved,
                    'scraped_at': datetime.now().isoformat()
                }
                
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                
                print("\n" + "=" * 60)
                print("📊 總覽統計")
                print("=" * 60)
                print(f"總共抓取: {len(all_articles)} 篇文章")
                print(f"總共儲存: {self.total_saved} 篇文章")
                if summary['year_range']['earliest']:
                    print(f"年份範圍: {summary['year_range']['earliest']} - {summary['year_range']['latest']}")
                print(f"各年份文章數:")
                for year in sorted(by_year.keys()):
                    print(f"  {year}: {len(by_year[year])} 篇")
                print(f"\n總覽檔案: {summary_file}")
            
            print("\n" + "=" * 60)
            print("✅ 爬取完成!")
            print("=" * 60)


async def main():
    print("🗞️  區塊客歷史新聞爬蟲")
    print("📅 涵蓋範圍: 2017~2025 年的所有文章")
    print("📄 頁碼說明: 頁碼 1 = 最新 (2025), 頁碼 1235 = 最舊 (2017)")
    print()
    
    # 輸入起始頁碼
    try:
        start_page = int(input("從第幾頁開始? (預設 1, 最新文章): ") or "1")
    except ValueError:
        start_page = 1
    
    # 輸入要爬取的頁數
    try:
        num_pages = int(input("要爬取幾頁? (預設 1235, 全部歷史): ") or "1235")
    except ValueError:
        num_pages = 1235
    
    print()
    print(f"🎯 將爬取頁碼 {start_page} → {start_page + num_pages - 1}")
    print(f"📊 預計文章數: ~{num_pages * 11:,} 篇")
    print()
    
    scraper = BlockcastHistoryScraper()
    await scraper.scrape(start_page=start_page, num_pages=num_pages)


if __name__ == "__main__":
    asyncio.run(main())
