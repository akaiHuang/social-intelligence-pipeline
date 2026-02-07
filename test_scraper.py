import asyncio
from scraper import XScraper, save_to_json


async def test_scraper():
    """測試爬蟲功能"""
    print("\n" + "=" * 60)
    print("X 爬蟲系統測試")
    print("=" * 60)
    
    # 使用 Elon Musk 的公開帳號進行測試
    test_url = "https://twitter.com/elonmusk"
    
    print(f"\n測試目標: {test_url}")
    print("爬取推文數量: 10 則（測試用）")
    print("模式: 顯示瀏覽器視窗\n")
    
    scraper = XScraper(headless=False)
    
    try:
        print("正在啟動瀏覽器...")
        await scraper.start()
        
        # 使用 .env 檔案中的帳號登入
        print("正在登入 X 平台...")
        await scraper.login()
        
        # 爬取資料
        data = await scraper.scrape_full_profile(test_url, max_tweets=10)
        
        # 儲存結果
        filepath = save_to_json(data, username='test', filename='test_result.json')
        
        print("\n" + "=" * 60)
        print("✅ 測試完成！")
        print("=" * 60)
        print(f"\n用戶名稱: {data['user']['name']}")
        print(f"用戶 ID: @{data['user']['username']}")
        print(f"簡介: {data['user']['bio'][:50]}..." if len(data['user']['bio']) > 50 else f"簡介: {data['user']['bio']}")
        print(f"關注數: {data['user']['following']}")
        print(f"粉絲數: {data['user']['followers']}")
        print(f"爬取推文數: {data['total_tweets_scraped']}")
        
        if data['tweets']:
            print(f"\n最新推文預覽:")
            print(f"  時間: {data['tweets'][0]['timestamp']}")
            print(f"  內容: {data['tweets'][0]['text'][:100]}...")
        
        print(f"\n資料已儲存至: {filepath}")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n正在關閉瀏覽器...")
        await scraper.close()
        print("完成！")


if __name__ == '__main__':
    asyncio.run(test_scraper())
