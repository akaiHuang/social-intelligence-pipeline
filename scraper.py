import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class XScraper:
    """X (Twitter) 爬蟲類別，使用 Playwright 進行瀏覽器自動化"""
    
    def __init__(self, headless: bool = False):
        """
        初始化爬蟲
        
        Args:
            headless: 是否使用無頭模式（不顯示瀏覽器）
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context = None
        self.cookies_file = 'x_cookies.json'
        
    async def start(self):
        """啟動瀏覽器"""
        self.playwright = await async_playwright().start()
        
        # 使用持久化上下文，保存瀏覽器資料（包含登入狀態）
        user_data_dir = './browser_data'
        os.makedirs(user_data_dir, exist_ok=True)
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=self.headless,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=['--disable-blink-features=AutomationControlled']
        )
        
        print("✓ 已啟動瀏覽器（使用持久化資料，會記住登入狀態）")
        
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        self.browser = self.context
        
        # 隱藏 webdriver 特徵
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    async def close(self):
        """關閉瀏覽器"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def login(self, username: str = None, password: str = None):
        """
        登入 X 平台（如果需要）
        
        Args:
            username: X 帳號
            password: X 密碼
        """
        username = username or os.getenv('X_USERNAME')
        password = password or os.getenv('X_PASSWORD')
        
        if not username or not password:
            print("未提供登入資訊，將以訪客模式繼續...")
            return
        
        try:
            print("正在前往登入頁面...")
            await self.page.goto('https://x.com/i/flow/login', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)
            
            # 輸入用戶名或email
            print("輸入帳號...")
            username_input = self.page.locator('input[autocomplete="username"]')
            await username_input.wait_for(timeout=10000)
            await username_input.fill(username)
            await asyncio.sleep(1)
            
            # 點擊 Next 按鈕
            print("點擊下一步...")
            next_button = self.page.locator('button:has-text("Next"), button:has-text("下一步")')
            await next_button.click()
            await asyncio.sleep(3)
            
            # 輸入密碼
            print("輸入密碼...")
            password_input = self.page.locator('input[type="password"]')
            await password_input.wait_for(timeout=10000)
            await password_input.fill(password)
            await asyncio.sleep(1)
            
            # 點擊登入按鈕
            print("點擊登入...")
            login_button = self.page.locator('button:has-text("Log in"), button:has-text("登入")')
            await login_button.click()
            await asyncio.sleep(5)
            
            print("✓ 登入成功")
        except Exception as e:
            print(f"登入失敗: {e}")
            print("將以訪客模式繼續...")
    
    async def scrape_user_profile(self, profile_url: str) -> Dict:
        """
        爬取用戶基本資料
        
        Args:
            profile_url: X 用戶頁面網址
            
        Returns:
            包含用戶資料的字典
        """
        await self.page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(5)
        
        # 滾動頁面以載入內容
        await self.page.evaluate('window.scrollTo(0, 400)')
        await asyncio.sleep(1)
        
        user_data = {}
        
        try:
            # 提取用戶名稱
            user_data['name'] = await self.page.locator('[data-testid="UserName"] span').first.text_content()
        except:
            user_data['name'] = 'Unknown'
        
        try:
            # 提取用戶 handle
            username_elem = await self.page.locator('[data-testid="UserName"]').text_content()
            if '@' in username_elem:
                user_data['username'] = username_elem.split('@')[1].split('\n')[0]
            else:
                user_data['username'] = profile_url.split('/')[-1]
        except:
            user_data['username'] = profile_url.split('/')[-1]
        
        try:
            # 提取簡介
            user_data['bio'] = await self.page.locator('[data-testid="UserDescription"]').text_content()
        except:
            user_data['bio'] = ''
        
        try:
            # 提取關注數、粉絲數等
            following_elem = await self.page.locator('a[href*="/following"] span').first.text_content()
            user_data['following'] = following_elem
        except:
            user_data['following'] = '0'
        
        try:
            followers_elem = await self.page.locator('a[href*="/verified_followers"] span').first.text_content()
            user_data['followers'] = followers_elem
        except:
            user_data['followers'] = '0'
        
        user_data['profile_url'] = profile_url
        user_data['scraped_at'] = datetime.now().isoformat()
        
        return user_data
    
    async def scrape_tweets(self, profile_url: str, max_tweets: int = 20) -> List[Dict]:
        """
        爬取用戶推文
        
        Args:
            profile_url: X 用戶頁面網址
            max_tweets: 最多爬取的推文數量
            
        Returns:
            推文列表
        """
        await self.page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(5)
        
        tweets = []
        seen_urls = set()
        scroll_count = 0
        max_scrolls = 500  # 大幅增加最大滾動次數
        no_new_tweets_count = 0
        last_tweet_count = 0
        
        print(f"開始爬取推文，目標: {max_tweets} 則...")
        print(f"將持續自動滾動直到達到目標數量...")
        
        # 等待推文載入
        try:
            await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
        except:
            print("  ⚠️ 未找到推文元素，可能需要登入或頁面結構已變更")
            return tweets
        
        while len(tweets) < max_tweets and scroll_count < max_scrolls and no_new_tweets_count < 10:
            # 提取當前頁面上的所有推文
            tweet_elements = await self.page.locator('article[data-testid="tweet"]').all()
            
            for tweet_elem in tweet_elements:
                if len(tweets) >= max_tweets:
                    break
                    
                try:
                    tweet_data = {}
                    
                    # 推文連結（用於去重）
                    try:
                        links = await tweet_elem.locator('a[href*="/status/"]').all()
                        if links:
                            tweet_url = await links[0].get_attribute('href')
                            full_url = f"https://twitter.com{tweet_url}"
                            
                            # 跳過已見過的推文
                            if full_url in seen_urls:
                                continue
                            
                            tweet_data['url'] = full_url
                            seen_urls.add(full_url)
                    except:
                        continue  # 沒有 URL 的跳過
                    
                    # 推文文字內容
                    try:
                        text_elem = tweet_elem.locator('[data-testid="tweetText"]')
                        tweet_data['text'] = await text_elem.text_content()
                    except:
                        tweet_data['text'] = ''
                    
                    # 推文時間
                    try:
                        time_elem = tweet_elem.locator('time')
                        tweet_data['timestamp'] = await time_elem.get_attribute('datetime')
                        display_time = await time_elem.text_content()
                        tweet_data['display_time'] = display_time
                    except:
                        tweet_data['timestamp'] = ''
                        tweet_data['display_time'] = ''
                    
                    # 互動數據：回覆、轉推、喜歡
                    try:
                        reply_elem = tweet_elem.locator('[data-testid="reply"]')
                        tweet_data['replies'] = await reply_elem.get_attribute('aria-label') or '0'
                    except:
                        tweet_data['replies'] = '0'
                    
                    try:
                        retweet_elem = tweet_elem.locator('[data-testid="retweet"]')
                        tweet_data['retweets'] = await retweet_elem.get_attribute('aria-label') or '0'
                    except:
                        tweet_data['retweets'] = '0'
                    
                    try:
                        like_elem = tweet_elem.locator('[data-testid="like"]')
                        tweet_data['likes'] = await like_elem.get_attribute('aria-label') or '0'
                    except:
                        tweet_data['likes'] = '0'
                    
                    # 只添加有文字內容的推文
                    if tweet_data.get('text') or tweet_data.get('url'):
                        tweets.append(tweet_data)
                        if len(tweets) % 10 == 0:  # 每 10 則顯示一次
                            print(f"  ✓ 已爬取 {len(tweets)}/{max_tweets} 則")
                        
                except Exception as e:
                    continue
            
            # 檢查本輪是否有新推文
            if len(tweets) == last_tweet_count:
                no_new_tweets_count += 1
                print(f"  ⚠️  第 {scroll_count + 1} 次滾動，無新推文 ({no_new_tweets_count}/10)")
            else:
                no_new_tweets_count = 0
                if len(tweets) % 10 != 0:  # 不是整十數時也顯示
                    print(f"  📊 第 {scroll_count + 1} 次滾動，目前共 {len(tweets)} 則")
            
            last_tweet_count = len(tweets)
            
            # 使用多種滾動方式確保頁面滾動
            if len(tweets) < max_tweets:
                print(f"  🔄 自動滾動第 {scroll_count + 1} 次...")
                # 方法1: 滾動到頁面底部
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
                
                # 方法2: 再滾動一次確保觸發載入
                await self.page.evaluate('window.scrollBy(0, 1000)')
                await asyncio.sleep(1)
            
            scroll_count += 1
        
        if no_new_tweets_count >= 10:
            print(f"  已連續 10 輪沒有新推文，停止滾動")
        
        print(f"✓ 完成！共爬取 {len(tweets)} 則推文")
        return tweets[:max_tweets]
    
    async def scrape_full_profile(self, profile_url: str, max_tweets: int = 20) -> Dict:
        """
        爬取完整的用戶資料（包含個人資料和推文）
        
        Args:
            profile_url: X 用戶頁面網址
            max_tweets: 最多爬取的推文數量
            
        Returns:
            完整的用戶資料字典
        """
        print(f"\n開始爬取: {profile_url}")
        print("=" * 60)
        
        # 爬取用戶資料
        print("\n[1/2] 爬取用戶基本資料...")
        user_data = await self.scrape_user_profile(profile_url)
        
        # 爬取推文
        print("\n[2/2] 爬取推文...")
        tweets = await self.scrape_tweets(profile_url, max_tweets)
        
        # 組合結果
        result = {
            'user': user_data,
            'tweets': tweets,
            'total_tweets_scraped': len(tweets)
        }
        
        return result


def save_to_json(data: Dict, username: str = None, filename: str = None):
    """
    將資料儲存為 JSON 檔案，按用戶名建立資料夾
    
    Args:
        data: 要儲存的資料
        username: 用戶名（用於建立資料夾）
        filename: 檔案名稱（如果不指定，會自動生成）
    """
    # 如果 username 是 None，從 data 中取得
    if not username:
        username = data.get('user', {}).get('username', 'unknown')
    
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"tweets_{timestamp}.json"
    
    # 建立用戶專屬資料夾
    user_folder = os.path.join('output', username)
    os.makedirs(user_folder, exist_ok=True)
    filepath = os.path.join(user_folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 資料已儲存至: {filepath}")
    return filepath


async def main():
    """主程式"""
    print("\n" + "=" * 60)
    print("X (Twitter) 爬蟲系統")
    print("=" * 60)
    
    # 取得用戶輸入
    profile_url = input("\n請輸入 X 用戶頁面網址 (例如: https://twitter.com/username): ").strip()
    
    if not profile_url:
        print("錯誤: 請提供有效的網址")
        return
    
    # 標準化網址格式
    if not profile_url.startswith('http'):
        profile_url = f"https://twitter.com/{profile_url}"
    
    # 詢問是否需要登入
    need_login = input("\n是否需要登入? (如果目標帳號有隱私設置) [y/N]: ").strip().lower()
    
    # 詢問要爬取的推文數量
    try:
        max_tweets = int(input("\n要爬取多少則推文? [預設: 20]: ").strip() or "20")
    except:
        max_tweets = 20
    
    # 詢問是否顯示瀏覽器
    show_browser = input("\n是否顯示瀏覽器視窗? [Y/n]: ").strip().lower()
    headless = show_browser == 'n'
    
    # 開始爬取
    scraper = XScraper(headless=headless)
    
    try:
        await scraper.start()
        
        # 如果需要登入
        if need_login == 'y':
            username = input("X 帳號: ").strip()
            password = input("X 密碼: ").strip()
            await scraper.login(username, password)
        
        # 爬取資料
        data = await scraper.scrape_full_profile(profile_url, max_tweets)
        
        # 儲存結果
        save_to_json(data)
        
        print("\n" + "=" * 60)
        print("爬取完成！")
        print("=" * 60)
        print(f"\n用戶名稱: {data['user']['name']}")
        print(f"用戶 ID: @{data['user']['username']}")
        print(f"關注數: {data['user']['following']}")
        print(f"粉絲數: {data['user']['followers']}")
        print(f"爬取推文數: {data['total_tweets_scraped']}")
        
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await scraper.close()


if __name__ == '__main__':
    asyncio.run(main())
