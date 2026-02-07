"""
X API 爬蟲腳本
使用官方 X API v2 抓取推文
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class XAPIScraper:
    def __init__(self):
        # 從環境變數讀取 API 憑證
        self.bearer_token = os.getenv('X_BEARER_TOKEN')
        if not self.bearer_token:
            raise ValueError("請在 .env 檔案中設定 X_BEARER_TOKEN")
        
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "v2UserTweetsPython"
        }
    
    def get_user_id(self, username):
        """
        根據使用者名稱取得 User ID
        
        Args:
            username: X 使用者名稱 (不含 @)
        
        Returns:
            user_id: 使用者 ID
        """
        url = f"{self.base_url}/users/by/username/{username}"
        
        params = {
            "user.fields": "id,name,username,created_at,description,public_metrics,verified"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            raise Exception(
                f"無法取得使用者資訊 (HTTP {response.status_code}): {response.text}"
            )
        
        data = response.json()
        print(f"✓ 找到使用者: @{data['data']['username']}")
        print(f"  名稱: {data['data']['name']}")
        print(f"  ID: {data['data']['id']}")
        print(f"  追蹤者: {data['data']['public_metrics']['followers_count']:,}")
        print()
        
        return data['data']['id'], data['data']
    
    def get_user_tweets(self, user_id, max_results=100, start_time=None):
        """
        取得使用者的推文
        
        Args:
            user_id: 使用者 ID
            max_results: 每次請求的最大結果數 (5-100,免費版可能有限制)
            start_time: 開始時間 (ISO 8601 格式,例如: 2020-01-01T00:00:00Z)
        
        Returns:
            tweets: 推文列表
        """
        url = f"{self.base_url}/users/{user_id}/tweets"
        
        # 設定請求參數
        params = {
            "max_results": min(max_results, 100),  # API 上限 100
            "tweet.fields": "id,text,created_at,author_id,public_metrics,referenced_tweets,entities",
            "expansions": "referenced_tweets.id,author_id",
            "user.fields": "username,name,verified"
        }
        
        # 如果指定開始時間 (需要 Basic 以上方案)
        if start_time:
            params["start_time"] = start_time
        
        all_tweets = []
        next_token = None
        page = 0
        
        print("🔍 開始抓取推文...")
        
        while True:
            page += 1
            
            if next_token:
                params["pagination_token"] = next_token
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"\n❌ API 請求失敗 (HTTP {response.status_code})")
                print(f"錯誤訊息: {response.text}")
                break
            
            data = response.json()
            
            # 檢查是否有資料
            if "data" not in data or not data["data"]:
                print("\n⚠️  沒有更多推文")
                break
            
            tweets = data["data"]
            all_tweets.extend(tweets)
            
            print(f"📄 第 {page} 頁: 取得 {len(tweets)} 則推文 (總計: {len(all_tweets)})")
            
            # 顯示最新和最舊的推文時間
            if tweets:
                oldest = tweets[-1]['created_at']
                newest = tweets[0]['created_at']
                print(f"   時間範圍: {oldest[:10]} ~ {newest[:10]}")
            
            # 檢查是否有下一頁
            if "meta" in data and "next_token" in data["meta"]:
                next_token = data["meta"]["next_token"]
            else:
                print("\n✓ 已抓取所有可用推文")
                break
        
        return all_tweets
    
    def save_tweets(self, tweets, user_data, filename=None):
        """
        儲存推文到 JSON 檔案
        
        Args:
            tweets: 推文列表
            user_data: 使用者資料
            filename: 檔案名稱 (可選)
        """
        if not filename:
            username = user_data['username']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.makedirs(f'output/{username}', exist_ok=True)
            filename = f'output/{username}/api_{timestamp}.json'
        
        # 整理資料格式
        output_data = {
            "user": user_data,
            "tweets": tweets,
            "metadata": {
                "total_tweets": len(tweets),
                "scraped_at": datetime.now().isoformat(),
                "method": "X API v2",
                "oldest_tweet": tweets[-1]['created_at'] if tweets else None,
                "newest_tweet": tweets[0]['created_at'] if tweets else None
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 已儲存到: {filename}")
        print(f"📊 共 {len(tweets)} 則推文")
        
        return filename


def main():
    """主程式"""
    print("=" * 60)
    print("X API 推文爬蟲")
    print("=" * 60)
    print()
    
    # 輸入使用者名稱
    username = input("請輸入 X 使用者名稱 (例如: elonmusk): ").strip()
    if not username:
        username = "elonmusk"  # 預設值
    
    # 移除 @ 符號
    username = username.replace('@', '')
    
    # 輸入要抓取的推文數量
    try:
        max_tweets = int(input("要抓取幾則推文? (免費版建議 100 以內): ") or "100")
    except ValueError:
        max_tweets = 100
    
    print()
    print("=" * 60)
    print()
    
    try:
        # 初始化爬蟲
        scraper = XAPIScraper()
        
        # 取得使用者 ID
        user_id, user_data = scraper.get_user_id(username)
        
        # 抓取推文
        tweets = scraper.get_user_tweets(user_id, max_results=max_tweets)
        
        if tweets:
            # 儲存結果
            scraper.save_tweets(tweets, user_data)
            
            print("\n" + "=" * 60)
            print("✅ 完成!")
            print("=" * 60)
        else:
            print("\n⚠️  沒有抓到任何推文")
    
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
