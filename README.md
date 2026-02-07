# Social Intelligence Pipeline

**Anti-Detection Social Data Collection at Scale**

A collection of purpose-built scrapers for harvesting social media and news intelligence while evading platform detection systems. Combines browser automation with human-behavior simulation to maintain persistent, undetectable data collection across X/Twitter and major news outlets.

---

## Why This Exists

Platforms like X (Twitter) and major news outlets aggressively detect and block automated access. Traditional scraping breaks within minutes. This pipeline uses anti-fingerprinting techniques, human-like browsing patterns, and persistent browser sessions to collect social intelligence data reliably over extended periods -- covering both social media profiles and multi-site news aggregation.

## Architecture

```
                    Social Intelligence Pipeline
                    ============================

  +------------------+     +------------------+     +------------------+
  | X/Twitter        |     | News Sites       |     | Crypto News      |
  | Browser Scraper  |     | (BlockTempo,     |     | Historical       |
  |                  |     |  ABMedia, etc.)  |     | Backfill         |
  +------------------+     +------------------+     +------------------+
          |                        |                        |
          v                        v                        v
    Playwright + Anti-Detection Layer
    (WebDriver masking, realistic UA, persistent context)
          |
          v
    Keyword Filtering & Matching Engine
          |
          v
    Structured JSON Output (output/)

  +------------------+
  | X API v2         |  <-- Official API path (Bearer Token)
  | (Parallel path)  |
  +------------------+
```

### How It Works

**X/Twitter Browser Collection (`scraper.py`)**
- Launches a persistent Chromium context that preserves login state across sessions.
- Masks WebDriver fingerprints (`navigator.webdriver` spoofing, automation flag removal).
- Uses realistic viewport (1920x1080) and Chrome-matching user agents.
- Scrapes user profiles (name, bio, follower counts) and tweet timelines (text, timestamps, engagement metrics).
- Supports both authenticated and guest-mode collection.

**X API v2 Collection (`x_api_scraper.py`)**
- Official Twitter API v2 integration for structured, rate-limit-aware data retrieval.
- Retrieves user profiles, tweet timelines, and public metrics with pagination support.
- Complementary path for when browser scraping is not required.

**Multi-Site News Scraping (`news_scraper.py` and variants)**
- Covers major crypto/blockchain news sources: BlockTempo, ABMedia, Blockcast, BTC Tech, and more.
- Configurable keyword filtering (BTC, Bitcoin, Elon Musk, Trump, Michael Saylor, CZ).
- Date-range targeting and full historical backfill capabilities.
- Resumable sessions for long-running collection jobs.

### Anti-Detection Techniques

| Technique | Implementation |
|-----------|---------------|
| WebDriver masking | `navigator.webdriver` set to `undefined` via init script |
| Automation flags | `--disable-blink-features=AutomationControlled` |
| Realistic fingerprint | Chrome-matching user agent, 1920x1080 viewport |
| Persistent sessions | `launch_persistent_context` with stored browser data |
| Human-like behavior | Randomized delays, progressive scroll loading |

## Tech Stack

- **Language**: Python 3.8+
- **Browser Automation**: Playwright (async API)
- **HTTP Client**: Requests (for API-based collection)
- **Async Runtime**: asyncio
- **Configuration**: python-dotenv

## Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure credentials (optional -- guest mode works without)
cp .env.example .env
# Edit .env: X_USERNAME, X_PASSWORD, X_BEARER_TOKEN

# Run X/Twitter browser scraper
python scraper.py

# Run multi-site news scraper
python news_scraper.py

# Run keyword-targeted search
python scrape_search_keywords.py

# Run historical backfill for specific sites
python scrape_multi_sites_history.py
```

### Output Format

Data is saved as structured JSON in the `output/` directory:

```json
{
  "user": {
    "name": "Display Name",
    "username": "handle",
    "bio": "Profile bio text",
    "followers": "1,234",
    "following": "567"
  },
  "tweets": [
    {
      "text": "Tweet content",
      "timestamp": "2025-11-14T09:00:00.000Z",
      "likes": "20 likes",
      "retweets": "10 retweets",
      "replies": "5 replies"
    }
  ]
}
```

## Project Structure

```
social-intelligence-pipeline/
  scraper.py                    # X/Twitter browser-based scraper (anti-detection)
  x_api_scraper.py              # X API v2 official endpoint scraper
  news_scraper.py               # Multi-site news aggregation scraper
  news_scraper_history.py       # Historical news backfill engine
  scrape_search_keywords.py     # Keyword-based search collection
  scrape_by_date.py             # Date-range targeted collection
  scrape_multi_sites_history.py # Multi-site historical scraping
  scrape_abmedia_*.py           # ABMedia-specific scrapers
  scrape_blocktempo_*.py        # BlockTempo-specific scrapers
  scrape_blockcast_history.py   # Blockcast historical scraper
  resume_*.py                   # Resumable long-running sessions
  test_*.py                     # Site-specific validation scripts
  requirements.txt              # Python dependencies
  API_SETUP.md                  # X API configuration guide
  NEWS_README.md                # News scraper documentation
```

---

Built by **Huang Akai (Kai)** -- Founder @ Universal FAW Labs | Creative Technologist | Ex-Ogilvy
