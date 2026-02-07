"""
多網站歷史新聞爬蟲
支援: BlockTempo, ABMedia (市場/比特幣)
從最後一頁往前爬取到第 1 頁，收集完整內文
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
import re

class MultiSiteHistoryScraper:
    def __init__(self):
        self.output_dir = 'output/news_history_multi'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 批次儲存設定
        self.batch_size = 30  # 每 30 篇寫入一次
        self.current_batch = []  # 當前批次的文章
        self.total_saved = 0  # 已儲存的文章總數
        
        # 時間追蹤 - 用於檢測廣告文章
        self.last_article_date = None  # 上一篇文章的日期
        
        # 網站設定
        self.sites_config = {
            'blockcast': {
                'name': 'Blockcast',
                'base_url': 'https://blockcast.it/category/news/page/',
                'start_page': 1235,  # 最後一頁
                'end_page': 1,  # 爬到第 1 頁
                'direction': 'backward',  # 往前爬（1235→1）
                'article_selector': 'article',
                'title_selector': 'a[rel="bookmark"], h3 a, h2 a, a',
                'link_selector': 'a[rel="bookmark"], h3 a, h2 a, a',
                'content_selector': '.entry-content',
                'skip_urls': [
                    'https://blockcast.it/2025/11/14/ethereum-interoperability-the-final-mile-to-mass-adoption/'
                ]
            },
            'blocktempo': {
                'name': 'BlockTempo',
                'base_url': 'https://www.blocktempo.com/category/cryptocurrency-market/exchange/page/',
                'start_page': 163,  # 最後一頁
                'end_page': 1,
                'article_selector': 'article, .post, .article-item',
                'title_selector': 'h2 a, h3 a, .entry-title a',
                'link_selector': 'h2 a, h3 a, .entry-title a',
                'content_selector': '.entry-content, .post-content, article .content'
            },
            'btctech': {
                'name': 'BlockTempo-BTCtech',
                'base_url': 'https://www.blocktempo.com/category/technology/technology-bitcoin/page/',
                'start_page': 109,  # 最後一頁
                'end_page': 1,
                'article_selector': 'article, .post, .article-item',
                'title_selector': 'h2 a, h3 a, .entry-title a',
                'link_selector': 'h2 a, h3 a, .entry-title a',
                'content_selector': '.entry-content, .post-content, article .content'
            },
            'marketanalytics': {
                'name': 'BlockTempo-MarketAnalytics',
                'base_url': 'https://www.blocktempo.com/category/cryptocurrency-market/market-analyze/page/',
                'start_page': 143,  # 最後一頁
                'end_page': 1,
                'article_selector': 'article, .post, .article-item',
                'title_selector': 'h2 a, h3 a, .entry-title a',
                'link_selector': 'h2 a, h3 a, .entry-title a',
                'content_selector': '.entry-content, .post-content, article .content'
            },
            'abmedia_market': {
                'name': 'ABMedia-市場',
                'base_url': 'https://abmedia.io/category/invsetments/market/page/',
                'start_page': 196,  # 最後一頁
                'end_page': 1,
                'article_selector': 'article, .post, .article-item',
                'title_selector': 'h2 a, h3 a, .entry-title a',
                'link_selector': 'h2 a, h3 a, .entry-title a',
                'content_selector': '.entry-content, .post-content, article .content'
            },
            'abmedia_bitcoin': {
                'name': 'ABMedia-比特幣',
                'base_url': 'https://abmedia.io/category/invsetments/bitcoin/page/',
                'start_page': 119,  # 最後一頁
                'end_page': 1,
                'article_selector': 'article, .post, .article-item',
                'title_selector': 'h2 a, h3 a, .entry-title a',
                'link_selector': 'h2 a, h3 a, .entry-title a',
                'content_selector': '.entry-content, .post-content, article .content'
            }
        }
    
    def _save_batch(self, site_name, force=False):
        """
        儲存當前批次的文章
        
        Args:
            site_name: 網站名稱
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
            if not year:
                year = 'unknown'  # 🔥 修復：沒有年份的文章存到 unknown 資料夾
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(article)
        
        # 儲存各年份
        for year in sorted(by_year.keys(), key=lambda x: (x == 'unknown', x)):
            articles = by_year[year]
            year_dir = os.path.join(self.output_dir, site_name, str(year))
            os.makedirs(year_dir, exist_ok=True)
            
            filename = os.path.join(year_dir, f'{site_name}_batch_{timestamp}.json')
            
            output_data = {
                'site': site_name,
                'year': year,
                'batch_articles': len(articles),
                'articles': articles,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 [{site_name}] [{year}] 已儲存 {len(articles)} 篇 → {filename}")
        
        self.total_saved += len(self.current_batch)
        print(f"✅ [{site_name}] 累計已儲存: {self.total_saved} 篇文章\n")
        
        # 清空當前批次
        self.current_batch = []
    
    def _is_advertisement(self, article_data, site_name, direction='backward'):
        """
        判斷文章是否為廣告
        使用時間連續性判斷：正常文章日期應該連續，廣告會突然跳到最新日期
        
        Args:
            article_data: 文章資料
            site_name: 網站名稱
            direction: 爬取方向 ('forward' 或 'backward')
            
        Returns:
            bool: True = 廣告, False = 正常文章
        """
        title = article_data.get('title', '')
        link = article_data.get('link', '')
        content = article_data.get('content', '')
        date_str = article_data.get('date', '')
        
        # 1. 標題過濾 - Podcast 節目
        if title.startswith('EP.'):
            print(f"    ⚠️  跳過 Podcast: {title[:50]}")
            return True
        
        # 2. URL 過濾 - 廣告連結
        if 'news-list?source=' in link or '/ep-' in link.lower():
            print(f"    ⚠️  跳過廣告連結: {link[:60]}")
            return True
        
        # 3. 內文長度過濾
        if len(content) < 300:
            print(f"    ⚠️  跳過短文章 ({len(content)} 字元): {title[:40]}")
            return True
        
        # 4. 固定文字過濾 - Podcast 固定開場白
        if '保證學不到東西的不負責任區塊鏈時事雜談' in content:
            print(f"    ⚠️  跳過 Podcast 內容: {title[:40]}")
            return True
        
        # 5. 時間連續性檢查（僅在 forward 模式啟用）
        # backward 模式（從舊到新）會自然產生時間跳躍，不應判定為廣告
        if direction == 'forward' and date_str and self.last_article_date:
            try:
                from datetime import datetime
                
                # 解析日期格式 (支援 2025/11/10 或 2025-11-10)
                current_date = None
                if '/' in date_str:
                    current_date = datetime.strptime(date_str, '%Y/%m/%d')
                elif '-' in date_str:
                    current_date = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                
                if current_date and self.last_article_date:
                    # 計算時間差（天數）
                    time_diff = abs((current_date - self.last_article_date).days)
                    
                    # 如果時間差超過 180 天（約 6 個月），判定為廣告
                    if time_diff > 180:
                        print(f"    ⚠️  時間跳躍過大 ({time_diff} 天): {date_str} → {self.last_article_date.strftime('%Y/%m/%d')}")
                        print(f"       跳過可能的廣告: {title[:40]}")
                        return True
                
                # 更新最後文章日期
                if current_date:
                    self.last_article_date = current_date
            
            except Exception as e:
                pass  # 日期解析失敗，繼續處理
        else:
            # 初始化最後文章日期
            if date_str:
                try:
                    from datetime import datetime
                    if '/' in date_str:
                        self.last_article_date = datetime.strptime(date_str, '%Y/%m/%d')
                    elif '-' in date_str:
                        self.last_article_date = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                except:
                    pass
        
        return False
    
    async def _fetch_article_content(self, page, article_url, site_name):
        """
        進入文章詳細頁面，抓取完整內文和年份
        
        Args:
            page: Playwright page 物件
            article_url: 文章網址
            site_name: 網站名稱
            
        Returns:
            dict: 包含完整內文、發布日期等資訊
        """
        try:
            print(f"    🔗 進入文章: {article_url[:80]}")
            await page.goto(article_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(1500)
            
            config = self.sites_config.get(site_name, {})
            
            # 抓取文章內文
            content = ''
            content_selectors = [
                config.get('content_selector', '.entry-content'),
                '.entry-content',
                '.post-content',
                '.article-content',
                'article .content',
                'main article'
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = await page.query_selector(selector)
                    if content_elem:
                        content = await content_elem.inner_text()
                        if content and len(content) > 100:
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
                        if text and len(text) > 20:
                            content_parts.append(text.strip())
                    except:
                        continue
                content = '\n\n'.join(content_parts)
            
            # 從 URL 提取年份
            year = None
            date = ''
            
            # 嘗試多種日期格式
            url_patterns = [
                r'/(\d{4})/(\d{2})/(\d{2})/',  # /2023/11/15/
                r'/(\d{4})-(\d{2})-(\d{2})/',  # /2023-11-15/
                r'/(\d{4})(\d{2})(\d{2})/',    # /20231115/
            ]
            
            for pattern in url_patterns:
                url_match = re.search(pattern, article_url)
                if url_match:
                    year = int(url_match.group(1))
                    month = url_match.group(2)
                    day = url_match.group(3)
                    date = f"{year}-{month}-{day}"
                    break
            
            # 如果 URL 沒有日期，嘗試從頁面抓取
            if not year:
                # 🔥 優先嘗試 meta 標籤 (BlockTempo 用這個)
                meta_elem = await page.query_selector('meta[property="article:published_time"]')
                if meta_elem:
                    date_text = await meta_elem.get_attribute('content')
                    if date_text:
                        # 解析 ISO 8601 格式: 2017-12-18T15:36:40+08:00
                        year_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if year_match:
                            year = int(year_match.group(1))
                            date = f"{year_match.group(1)}/{year_match.group(2)}/{year_match.group(3)}"
                
                # 如果 meta 沒有，再試其他選擇器
                if not year:
                    date_elem = await page.query_selector('time, .post-date, .entry-date, [datetime]')
                    if date_elem:
                        date_text = await date_elem.inner_text() or await date_elem.get_attribute('datetime')
                        if date_text:
                            year_match = re.search(r'20\d{2}', date_text)
                            if year_match:
                                year = int(year_match.group())
                            date = date_text
            
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
    
    async def scrape_site(self, page, site_key, start_page=None, num_pages=None):
        """
        爬取指定網站的歷史文章
        
        Args:
            page: Playwright page 物件
            site_key: 網站識別碼
            start_page: 起始頁碼
            num_pages: 要爬取的頁數
        """
        config = self.sites_config[site_key]
        site_name = config['name']
        direction = config.get('direction', 'backward')  # 預設往前爬
        skip_urls = config.get('skip_urls', [])
        
        # 🔥 重置時間追蹤（每個網站獨立追蹤）
        self.last_article_date = None
        
        # 使用設定的起始頁碼，或從參數覆蓋
        if start_page is None:
            start_page = config['start_page']
        
        # 計算結束頁碼和頁數範圍
        if direction == 'forward':
            # 往後爬（1→1235）
            if num_pages:
                end_page = min(start_page + num_pages - 1, config['end_page'])
            else:
                end_page = config['end_page']
            page_range = range(start_page, end_page + 1)
            total_pages = end_page - start_page + 1
        else:
            # 往前爬（163→1）
            if num_pages:
                end_page = max(start_page - num_pages + 1, config['end_page'])
            else:
                end_page = config['end_page']
            page_range = range(start_page, end_page - 1, -1)
            total_pages = start_page - end_page + 1
        
        print(f"\n🔍 正在爬取：{site_name}")
        print("=" * 60)
        print(f"起始頁: 第 {start_page} 頁")
        print(f"結束頁: 第 {end_page} 頁")
        print(f"方向: {'往後' if direction == 'forward' else '往前'}")
        print(f"目標: 爬取 {total_pages} 頁")
        print("=" * 60)
        
        all_articles = []
        
        # 根據方向爬取
        for page_num in page_range:
            try:
                url = f"{config['base_url']}{page_num}/"
                
                print(f"\n📄 第 {page_num} 頁: {url}")
                
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(2000)
                
                # 爬取文章列表
                article_elements = await page.query_selector_all(config['article_selector'])
                
                if not article_elements:
                    print(f"⚠️  第 {page_num} 頁沒有找到文章")
                    continue
                
                print(f"找到 {len(article_elements)} 篇文章")
                
                # 先收集所有文章的基本資訊
                article_links = []
                
                for elem in article_elements:
                    try:
                        # 提取標題和連結
                        link_elem = await elem.query_selector(config['link_selector'])
                        if link_elem:
                            link = await link_elem.get_attribute('href')
                            title = await link_elem.inner_text()
                            
                            # 如果沒找到標題，再試其他選擇器
                            if not title:
                                title_elem = await elem.query_selector('h1, h2, h3, h4, .title')
                                title = await title_elem.inner_text() if title_elem else ''
                            
                            if link and not link.startswith('http'):
                                # 補全網址
                                if 'blocktempo' in site_key or 'btctech' in site_key or 'marketanalytics' in site_key:
                                    link = f"https://www.blocktempo.com{link}"
                                elif 'abmedia' in site_key:
                                    link = f"https://abmedia.io{link}"
                                elif 'blockcast' in site_key:
                                    link = f"https://blockcast.it{link}"
                            
                            # 🔥 檢查是否為要跳過的 URL（置頂文章）
                            if link in skip_urls:
                                print(f"    ⚠️  跳過置頂文章: {title[:40] if title else link[:60]}")
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
                        continue
                
                print(f"成功收集 {len(article_links)} 篇文章連結")
                
                # 逐一進入文章頁面抓取完整內容
                page_articles = []
                for idx, article_info in enumerate(article_links, 1):
                    try:
                        print(f"\n  [{idx}/{len(article_links)}] {article_info['title'][:50]}...")
                        
                        # 進入文章詳細頁面
                        article_details = await self._fetch_article_content(page, article_info['link'], site_key)
                        
                        # 從 URL 提取年份（備用）
                        year = None
                        date = ''
                        url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', article_info['link'])
                        if url_match:
                            year = int(url_match.group(1))
                            date = f"{url_match.group(1)}/{url_match.group(2)}/{url_match.group(3)}"
                        
                        # 優先使用文章頁面的年份
                        final_year = article_details['year'] if article_details['year'] else year
                        final_date = article_details['date'] if article_details['date'] else date
                        
                        article_data = {
                            'title': article_info['title'],
                            'link': article_info['link'],
                            'summary': article_info['summary'],
                            'content': article_details['content'],
                            'date': final_date,
                            'year': final_year,
                            'source': site_name,
                            'page_num': page_num,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        # 🔥 檢查是否為廣告（傳入爬取方向）
                        if self._is_advertisement(article_data, site_name, direction):
                            continue
                        
                        page_articles.append(article_data)
                        all_articles.append(article_data)
                        
                        # 加入批次
                        self.current_batch.append(article_data)
                        
                        # 顯示進度
                        year_info = f"[{final_year}]" if final_year else "[?]"
                        content_len = len(article_details['content'])
                        print(f"  ✓ {year_info} 抓取成功 (內文: {content_len} 字元)")
                        
                        # 達到批次大小時自動儲存
                        if len(self.current_batch) >= self.batch_size:
                            print(f"\n{'='*60}")
                            print(f"📦 已累積 {len(self.current_batch)} 篇文章，開始批次儲存...")
                            print(f"{'='*60}")
                            self._save_batch(site_name)
                    
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
        
        # 爬取完成後，強制儲存剩餘的文章
        if self.current_batch:
            print(f"\n{'='*60}")
            print(f"📦 [{site_name}] 爬取完成！儲存剩餘 {len(self.current_batch)} 篇文章...")
            print(f"{'='*60}")
            self._save_batch(site_name, force=True)
        
        print(f"\n✅ [{site_name}] 共成功抓取: {len(all_articles)} 篇文章")
        print(f"💾 [{site_name}] 總共儲存: {self.total_saved} 篇文章")
        
        return all_articles
    
    async def scrape_all_sites(self, sites=None, num_pages=None):
        """
        爬取所有網站或指定網站
        
        Args:
            sites: 要爬取的網站列表 ['blocktempo', 'abmedia_market', 'abmedia_bitcoin']
                   如果為 None，則爬取所有網站
            num_pages: 每個網站要爬取的頁數（從最後一頁往前）
        """
        if sites is None:
            sites = list(self.sites_config.keys())
        
        print("=" * 60)
        print("🚀 開始多網站歷史新聞爬取")
        print("=" * 60)
        print(f"目標網站: {', '.join([self.sites_config[s]['name'] for s in sites])}")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # 🔥 無頭模式，不顯示視窗
            page = await browser.new_page()
            
            all_results = {}
            
            try:
                for site_key in sites:
                    print(f"\n\n{'='*60}")
                    print(f"開始爬取: {self.sites_config[site_key]['name']}")
                    print(f"{'='*60}")
                    
                    # 重置批次計數
                    self.current_batch = []
                    self.total_saved = 0
                    self.last_article_date = None  # 🔥 重置時間追蹤
                    
                    articles = await self.scrape_site(page, site_key, num_pages=num_pages)
                    all_results[site_key] = articles
                    
                    print(f"\n✅ {self.sites_config[site_key]['name']} 完成！")
                    print(f"   共抓取 {len(articles)} 篇文章")
                    
            except Exception as e:
                print(f"\n❌ 爬取過程發生錯誤: {e}")
            
            finally:
                await browser.close()
            
            # 生成總覽報告
            print("\n" + "=" * 60)
            print("📊 所有網站爬取完成！")
            print("=" * 60)
            for site_key, articles in all_results.items():
                print(f"{self.sites_config[site_key]['name']}: {len(articles)} 篇文章")
            print("=" * 60)
            
            return all_results


async def main():
    print("🗞️  多網站歷史新聞爬蟲")
    print("=" * 60)
    print("支援網站:")
    print("  1. Blockcast 區塊客 (1235 頁)")
    print("  2. BlockTempo 交易所分類 (163 頁)")
    print("  3. BlockTempo-BTCtech 比特幣技術分類 (109 頁)")
    print("  4. BlockTempo-MarketAnalytics 市場分析分類 (143 頁)")
    print("  5. ABMedia 投資市場 (196 頁)")
    print("  6. ABMedia 比特幣 (119 頁)")
    print("=" * 60)
    print()
    
    scraper = MultiSiteHistoryScraper()
    
    # 🔥 完整模式：爬取所有歷史頁面
    print("🔥 完整模式：爬取所有歷史頁面（共 1,965 頁）")
    await scraper.scrape_all_sites()  # 不傳 num_pages 參數 = 爬取全部


if __name__ == "__main__":
    asyncio.run(main())
