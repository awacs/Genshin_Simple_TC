# Genshin_Simple_TC
Simple_genshin_tc

## Web Scraper with Tiered Approach

A Python-based web scraper that uses a tiered approach to scrape websites with different strategies:

1. **Tier 1: API/HTML/JSON** - Try to scrape using direct HTTP requests and parsing HTML/JSON
2. **Tier 2: Playwright SPA** - If Tier 1 fails, use Playwright to handle Single Page Applications
3. **Tier 3: Visual AI** - Placeholder for future implementation using computer vision and OCR

### Target Website

This scraper is designed to scrape data from https://app.yshelper.com/#/pages/rank2/rank2, which appears to be a Single Page Application (SPA). The scraper will automatically try different approaches until it successfully extracts the data.

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

#### Basic Usage

Run the scraper with the default URL (https://app.yshelper.com/#/pages/rank2/rank2):
```bash
python scraper.py
```

Or specify a custom URL:
```bash
python scraper.py "https://example.com"
```

#### Example Usage for Target Website

Use the provided example script:
```bash
python example_usage.py
```

This will scrape the yshelper.com rank page and save the data to the `scraped_data/` directory.

#### Demo Mode

To test the scraper functionality with a local test file:
```bash
python demo.py
```

This demonstrates all tiers of scraping and verifies the installation is working correctly.

#### Test Suite

To run the validation test suite:
```bash
python test_validation.py
```

This tests:
- Case-insensitive keyword matching (lowercase, Mixed Case, UPPERCASE)
- Rejection of "Please enable JavaScript" messages
- Proper fallback from Tier 1 to Tier 2 for SPAs

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
   - **Validates the scraped data** to ensure it contains expected content

2. If Tier 1 fails, it tries Tier 2 (Playwright SPA)
   - Launches a headless browser
   - Waits for page to load including dynamic content
   - Extracts text and looks for JavaScript data objects
   - Saves both text and HTML content
   - **Validates the scraped data** to ensure it contains expected content

3. If Tier 2 fails, it would try Tier 3 (not yet implemented)
   - Would use computer vision and OCR for visual scraping

### Data Validation

The scraper includes intelligent validation to ensure the scraped data is actually useful:

**Rejection Criteria:**
- Rejects pages with "Please enable JavaScript to continue" messages
- Rejects pages that don't contain expected data fields

**Acceptance Criteria:**
- Must contain at least 3 out of 5 expected keywords:
  - "rank" (case-insensitive: rank, Rank, RANK)
  - "team comp" (case-insensitive: team comp, Team Comp, TEAM COMP)
  - "use rate" (case-insensitive)
  - "own rate" (case-insensitive)
  - "room ratio" (case-insensitive)

This validation ensures that the scraper automatically falls back from Tier 1 to Tier 2 when encountering Single Page Applications that require JavaScript execution.

### Example Output Structure

```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "text": "Page content...",
  "scraped_at": "2024-01-01T12:00:00"
}
```

### Troubleshooting

**Tier 1 fails (DNS/Connection errors)**
- The website may not be accessible from your network
- Check if you can access the website in a browser
- Try using Tier 2 which might handle redirects better

**Tier 2 fails (Playwright not installed)**
```bash
pip install playwright
playwright install chromium
```

**All tiers fail**
- Verify the website is accessible
- Check if the website requires authentication
- The website may have anti-scraping measures
- Try adjusting the wait times in the Playwright section of the code

### Project Structure

```
.
├── scraper.py          # Main scraper with tiered approach
├── example_usage.py    # Example for scraping the target website
├── demo.py            # Demo script to test functionality
├── requirements.txt   # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore file
└── scraped_data/      # Output directory (created automatically)
    ├── *.txt          # Text format output
    └── *.json         # JSON format output
```
