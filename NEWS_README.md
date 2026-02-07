# 加密貨幣新聞爬蟲使用指南

## 📰 支援的新聞網站

1. **動區動趨 (BlockTempo)** - https://www.blocktempo.com
2. **鏈新聞 (ABMedia)** - https://abmedia.io
3. **區塊客 (Blockcast)** - https://blockcast.it
4. **鉅亨網區塊鏈** - https://news.cnyes.com/news/cat/bc

---

## 🔑 預設關鍵字

新聞爬蟲會自動篩選包含以下關鍵字的文章:

### Bitcoin 相關:
- BTC
- Bitcoin
- 比特幣
- 比特币

### 意見領袖:
- **Elon Musk** (馬斯克, 马斯克)
- **Trump** (川普, 特朗普)
- **Michael Saylor**
- **CZ** (趙長鵬)

---

## 📂 檔案結構

爬取的新聞會自動分類儲存到:

```
output/
└── news/
    ├── bitcoin/          # BTC 相關新聞
    ├── elon_musk/        # Elon Musk 相關新聞
    ├── trump/            # 川普相關新聞
    ├── saylor/           # Michael Saylor 相關新聞
    ├── cz/               # CZ 相關新聞
    ├── other/            # 其他相關新聞
    └── summary_*.json    # 總覽統計
```

每個分類資料夾內的檔案格式:
```
news_20251115_143022.json
```

---

## 🚀 使用方式

### 執行爬蟲:
```bash
python news_scraper.py
```

### 自訂關鍵字 (修改 news_scraper.py):
```python
self.keywords = [
    'BTC', 'Bitcoin',
    'your_custom_keyword',  # 新增你的關鍵字
]
```

---

## 📊 輸出格式

### 文章 JSON 格式:
```json
{
  "category": "bitcoin",
  "total_articles": 25,
  "articles": [
    {
      "title": "比特幣突破10萬美元...",
      "link": "https://...",
      "summary": "文章摘要...",
      "date": "2025-11-15",
      "source": "BlockTempo",
      "scraped_at": "2025-11-15T14:30:22"
    }
  ],
  "keywords": ["BTC", "Bitcoin", ...],
  "scraped_at": "2025-11-15T14:30:22"
}
```

### 總覽 JSON 格式:
```json
{
  "total_articles": 95,
  "by_category": {
    "bitcoin": 45,
    "elon_musk": 12,
    "trump": 18,
    "saylor": 8,
    "cz": 7,
    "other": 5
  },
  "by_source": {
    "BlockTempo": 32,
    "ABMedia": 28,
    "Blockcast": 20,
    "Cnyes": 15
  },
  "scraped_at": "2025-11-15T14:30:22"
}
```

---

## ⚙️ 進階設定

### 調整每個網站的抓取數量:
```python
# 在 scrape_all() 中修改
articles = await self.scrape_blocktempo(page, max_articles=100)  # 預設 50
```

### 新增其他網站:
```python
async def scrape_your_site(self, page, max_articles=50):
    """爬取你的網站"""
    url = "https://your-site.com"
    # 實作爬取邏輯
```

---

## 🔍 爬取流程

1. **啟動無頭瀏覽器** (Chromium)
2. **依序爬取** 4 個新聞網站
3. **關鍵字篩選** 只保留相關文章
4. **自動分類** 根據內容分到對應資料夾
5. **生成統計** 總覽各類別和來源的文章數量

---

## 📌 注意事項

- 爬蟲使用 **無頭模式** (headless=True),不會開啟瀏覽器視窗
- 每個網站之間有 **3 秒延遲**,避免請求過快
- 文章摘要會自動 **截斷至 200 字元**
- 重複執行會產生 **不同時間戳記的檔案**,不會覆蓋

---

## 🆚 與 X 爬蟲比較

| 功能 | X 爬蟲 | 新聞爬蟲 |
|------|--------|----------|
| 目標 | 社群媒體推文 | 新聞文章 |
| 限制 | 3-4 個月歷史 | 網站首頁即時新聞 |
| 分類 | 按使用者 | 按關鍵字主題 |
| 速度 | 較慢 (需滾動) | 較快 |
| 穩定性 | 可能被限制 | 較穩定 |

---

## 💡 使用建議

### 定期執行:
```bash
# 每天定時抓取新聞
# 可用 cron job 或 Task Scheduler
0 9 * * * cd /path/to/x && python news_scraper.py
```

### 搭配 X 爬蟲使用:
1. 用 **新聞爬蟲** 追蹤即時新聞和趨勢
2. 用 **X 爬蟲** 深入追蹤特定人物的言論

---

## 🐛 常見問題

### Q: 為什麼沒有抓到文章?
A: 檢查關鍵字是否太嚴格,或網站結構已改變

### Q: 如何新增更多關鍵字?
A: 修改 `news_scraper.py` 中的 `self.keywords` 列表

### Q: 可以只爬特定網站嗎?
A: 在 `scrape_all()` 中註解掉不需要的網站

### Q: 如何增加爬取深度?
A: 調整 `max_articles` 參數 (預設 50)

---

## 📧 輸出範例

執行後會看到類似輸出:
```
🔍 正在爬取：動區動趨 (BlockTempo)
============================================================
📄 找到 48 個文章元素
  ✓ 比特幣突破10萬美元創歷史新高...
  ✓ 川普提名親加密貨幣人選...
  ✓ Elon Musk旗下X平台將支援加密支付...

✅ BlockTempo: 找到 23 篇相關文章

💾 bitcoin: 已儲存 45 篇文章到 output/news/bitcoin/news_20251115_143022.json
💾 elon_musk: 已儲存 12 篇文章到 output/news/elon_musk/news_20251115_143022.json

📊 總覽: output/news/summary_20251115_143022.json
總共 95 篇文章
分類統計: {'bitcoin': 45, 'elon_musk': 12, 'trump': 18, ...}
來源統計: {'BlockTempo': 32, 'ABMedia': 28, ...}
```
