# Genshin_Simple_TC
Simple_genshin_tc

## Web Scraper with Tiered Approach

A Python-based web scraper that uses a tiered approach to scrape websites with different strategies:

1. **Tier 1: API/HTML/JSON** - Try to scrape using direct HTTP requests and parsing HTML/JSON
2. **Tier 2: Playwright SPA** - If Tier 1 fails, use Playwright to handle Single Page Applications
3. **Tier 3: Visual AI** - Placeholder for future implementation using computer vision and OCR

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers (required for Tier 2):
```bash
playwright install chromium
```

### Usage

Run the scraper with the default URL (https://app.yshelper.com/#/pages/rank2/rank2):
```bash
python scraper.py
```

Or specify a custom URL:
```bash
python scraper.py "https://example.com"
```

### Output

The scraper saves data in two formats in the `scraped_data/` directory:
- **Text file (.txt)** - Human-readable format with URL, title, and content
- **JSON file (.json)** - Structured data format for programmatic access

### How It Works

1. The scraper tries Tier 1 first (API/HTML/JSON approach)
   - Makes HTTP request to the URL
   - Checks if response is JSON
   - Parses HTML and looks for embedded JSON in script tags
   - Extracts text content from HTML

2. If Tier 1 fails, it tries Tier 2 (Playwright SPA)
   - Launches a headless browser
   - Waits for page to load including dynamic content
   - Extracts text and looks for JavaScript data objects
   - Saves both text and HTML content

3. If Tier 2 fails, it would try Tier 3 (not yet implemented)
   - Would use computer vision and OCR for visual scraping

### Example Output Structure

```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "text": "Page content...",
  "scraped_at": "2024-01-01T12:00:00"
}
```
