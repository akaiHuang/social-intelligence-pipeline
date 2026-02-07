import asyncio
import json
from datetime import datetime
from scraper import XScraper


async def scrape_with_date_filter():
    """爬取特定日期範圍的推文"""
    print("\n" + "=" * 60)
    print("X 爬蟲系統 - 日期篩選模式")
    print("=" * 60)
    
    # 設定參數
    profile_url = input("\n請輸入 X 用戶網址 [預設: https://x.com/elonmusk]: ").strip()
    if not profile_url:
        profile_url = "https://x.com/elonmusk"
    elif not profile_url.startswith('http'):
        profile_url = f"https://twitter.com/{profile_url}"
    
    try:
        max_tweets = int(input("要爬取多少則推文? [預設: 2000]: ").strip() or "2000")
    except:
        max_tweets = 2000
    
    start_year = input("從哪一年開始? [預設: 2020]: ").strip() or "2020"
    
    print(f"\n設定:")
    print(f"  目標: {profile_url}")
    print(f"  爬取數量: {max_tweets} 則")
    print(f"  日期篩選: {start_year} 年之後")
    print(f"  登入: 是（使用 .env 中的帳號）")
    
    scraper = XScraper(headless=False)
    
    try:
        print("\n正在啟動瀏覽器...")
        await scraper.start()
        
        print("\n" + "=" * 60)
        print("⚠️  重要提示：")
        print("為了爬取更多歷史推文，請在瀏覽器中手動登入 X 帳號")
        print("登入後按 Enter 繼續...")
        print("=" * 60)
        input("\n按 Enter 繼續...")
        
        print("✓ 繼續執行...")
        
        print(f"\n開始爬取 {profile_url}")
        print("=" * 60)
        
        # 爬取用戶資料
        print("\n[1/2] 爬取用戶基本資料...")
        user_data = await scraper.scrape_user_profile(profile_url)
        
        # 爬取推文
        print(f"\n[2/2] 爬取推文（目標 {max_tweets} 則）...")
        all_tweets = await scraper.scrape_tweets(profile_url, max_tweets)
        
        # 篩選日期
        print(f"\n正在篩選 {start_year} 年之後的推文...")
        filtered_tweets = []
        for tweet in all_tweets:
            if tweet.get('timestamp'):
                tweet_year = tweet['timestamp'][:4]  # 取得年份
                if int(tweet_year) >= int(start_year):
                    filtered_tweets.append(tweet)
        
        print(f"✓ 篩選完成: {len(filtered_tweets)}/{len(all_tweets)} 則符合條件")
        
        # 組合結果
        result = {
            'user': user_data,
            'tweets': filtered_tweets,
            'total_tweets_scraped': len(all_tweets),
            'filtered_tweets_count': len(filtered_tweets),
            'filter_criteria': f"從 {start_year} 年開始",
            'scraped_at': datetime.now().isoformat()
        }
        
        # 儲存結果
        username = user_data.get('username', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"from{start_year}_{timestamp}.json"
        
        import os
        from scraper import save_to_json
        filepath = save_to_json(result, username, filename)
        
        print("\n" + "=" * 60)
        print("✅ 爬取完成！")
        print("=" * 60)
        print(f"\n用戶: {user_data['name']} (@{user_data['username']})")
        print(f"總共爬取: {len(all_tweets)} 則推文")
        print(f"符合條件: {len(filtered_tweets)} 則（{start_year} 年後）")
        print(f"\n儲存位置: {filepath}")
        
        if filtered_tweets:
            print(f"\n最新推文:")
            print(f"  時間: {filtered_tweets[0].get('display_time', 'N/A')}")
            print(f"  內容: {filtered_tweets[0]['text'][:80]}...")
            
            print(f"\n最舊推文:")
            print(f"  時間: {filtered_tweets[-1].get('display_time', 'N/A')}")
            print(f"  內容: {filtered_tweets[-1]['text'][:80]}...")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n正在關閉瀏覽器...")
        await scraper.close()
        print("完成！")


if __name__ == '__main__':
    asyncio.run(scrape_with_date_filter())
