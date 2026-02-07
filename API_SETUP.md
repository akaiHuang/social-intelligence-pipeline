# X API 設定指南

## 📋 方案比較

| 方案 | 價格 | 功能 | 適用情境 |
|------|------|------|----------|
| **網頁爬蟲** | 免費 | 只能抓最近 3-4 個月 | 測試、近期資料 |
| **API Free** | 免費 | 最近推文,無歷史搜尋 | 基本測試 |
| **API Basic** | $200/月 | 15,000 發文/月,無歷史搜尋 | 一般應用 |
| **API Pro** | $5,000/月 | 完整歷史搜尋 | 需要 2020+ 資料 |

---

## 🚀 如何取得 X API Bearer Token

### 步驟 1: 申請開發者帳號

1. 前往 [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. 使用您的 X 帳號登入
3. 點擊 "Sign up for Free Account"
4. 填寫申請表單:
   - 選擇用途 (例如: Building tools for X users)
   - 說明如何使用 API
   - 同意開發者條款

### 步驟 2: 建立 App

1. 登入後,點擊 "Projects & Apps" → "Overview"
2. 點擊 "+ Create App"
3. 輸入 App 名稱 (例如: "My X Scraper")
4. 記下您的 **API Key** 和 **API Secret** (只會顯示一次!)

### 步驟 3: 產生 Bearer Token

**方法 A: 在 Developer Portal 產生**
1. 進入您的 App 設定頁面
2. 點擊 "Keys and tokens" 標籤
3. 在 "Authentication Tokens" 區塊點擊 "Generate"
4. 複製 **Bearer Token** (只會顯示一次!)

**方法 B: 使用 API Key/Secret 產生**
```bash
# 使用 curl 產生 Bearer Token
curl -u 'API_KEY:API_SECRET' \
  --data 'grant_type=client_credentials' \
  'https://api.twitter.com/oauth2/token'
```

### 步驟 4: 設定環境變數

1. 複製 `.env.example` 為 `.env`:
```bash
cp .env.example .env
```

2. 編輯 `.env` 檔案,填入您的 Bearer Token:
```
X_BEARER_TOKEN=your_actual_bearer_token_here
```

⚠️ **注意**: `.env` 檔案已加入 `.gitignore`,不會上傳到 Git

---

## 🧪 測試 API

安裝相依套件 (如果還沒安裝):
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

執行 API 爬蟲:
```bash
python x_api_scraper.py
```

---

## 📊 免費版限制

根據官方文件,**Free tier** 有以下限制:

### ✅ 可用功能:
- 取得使用者資訊
- 取得使用者最近的推文 (timeline)
- 每月 100 則發文額度

### ❌ 不可用功能:
- **無法搜尋歷史推文** (需要 Pro 方案 $5,000/月)
- 無法使用 Filtered Stream
- 無法使用 Full-archive search

### 📉 Rate Limits (速率限制):
- User lookup: 300 requests / 15分鐘
- User tweets: 1,500 requests / 15分鐘
- 每次請求最多 100 則推文

---

## 🆚 兩種方案比較

### 方案 1: 網頁爬蟲 (Playwright)
**檔案**: `scrape_by_date.py`

**優點**:
- ✅ 完全免費
- ✅ 不需要 API 申請
- ✅ 可以抓到互動數據 (按讚、轉推、回覆)

**缺點**:
- ❌ 只能抓最近 3-4 個月
- ❌ 速度較慢 (需要滾動載入)
- ❌ 可能被平台偵測/限制

**使用情境**: 測試用途、只需要近期資料

---

### 方案 2: X API v2
**檔案**: `x_api_scraper.py`

**優點**:
- ✅ 官方支援,穩定可靠
- ✅ 速度快,結構化資料
- ✅ 有 rate limit 但很寬鬆

**缺點**:
- ❌ 免費版無法抓歷史推文 (2020+)
- ❌ 需要申請開發者帳號
- ❌ Pro 方案很貴 ($5,000/月)

**使用情境**: 
- Free tier: 基本測試、最近推文
- Pro tier: 需要完整歷史資料

---

## 💡 建議

### 如果預算有限:
1. **先用網頁爬蟲** (`scrape_by_date.py`) 抓最近 3-4 個月
2. **定期執行** (例如每週),逐步累積歷史資料
3. 未來就能建立完整的推文資料庫

### 如果需要完整歷史:
1. 考慮使用 **第三方工具**:
   - [snscrape](https://github.com/JustAnotherArchivist/snscrape) (免費,但可能不穩定)
   - [Apify Twitter Scraper](https://apify.com/apify/twitter-scraper) (付費,但比 API 便宜)
2. 或直接付費使用 **X API Pro** ($5,000/月)

---

## 🔗 相關連結

- [X API 文件](https://developer.twitter.com/en/docs/twitter-api)
- [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [API 定價](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api)
- [Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
