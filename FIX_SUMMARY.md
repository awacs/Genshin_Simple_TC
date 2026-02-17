# SPA Shell Detection Fix - Summary

## Problem
The Tier 1 scraper was treating SPA shell responses (containing only "please enable javascript" messages) as successful scrapes, preventing Tier 2 (Playwright with JS execution) from running.

## Before the Fix
```
URL: https://app.yshelper.com/#/pages/rank2/rank2
    ↓
[Tier 1] Fetch HTML → Status 200 ✓
    ↓
[Tier 1] Extract text → "Please enable JavaScript" ✓
    ↓
[Tier 1] Return data ✓ (WRONG - this is just an SPA shell!)
    ↓
scraper.scrape() → Success!
    ↓
Output file contains: "Please enable JavaScript" (useless)
    ↓
[Tier 2] NEVER RUNS ✗
```

## After the Fix
```
URL: https://app.yshelper.com/#/pages/rank2/rank2
    ↓
[Tier 1] Fetch HTML → Status 200 ✓
    ↓
[Tier 1] Extract text → "Please enable JavaScript"
    ↓
[Tier 1] _is_spa_shell() check:
    - Contains "please enable javascript"? YES ✓
    - Is content too short? Possibly ✓
    - Has noscript tags? Possibly ✓
    ↓
[Tier 1] SPA shell detected! → Return None ✗
    ↓
[Tier 2] Attempting Playwright SPA scraping... ✓
    ↓
[Tier 2] Launch browser with JS enabled
    ↓
[Tier 2] Wait for dynamic content to load
    ↓
[Tier 2] Extract real data → Character rankings, ratios, etc. ✓
    ↓
scraper.scrape() → Success!
    ↓
Output file contains: Real data from the SPA ✓
```

## Detection Heuristics

The fix adds three heuristics to detect SPA shells:

1. **JavaScript Error Messages** (9 variations detected):
   - "please enable javascript"
   - "javascript is disabled"
   - "javascript is required"
   - "enable javascript"
   - "require javascript"
   - "javascript off"
   - "turn on javascript"
   - "javascript must be enabled"
   - "please turn on javascript"

2. **Content Length Check**:
   - If text content < 200 characters → likely an SPA shell

3. **Noscript Content**:
   - If noscript tags contain > 50 characters → likely an SPA requiring JS

## Code Changes

### New Constants
```python
SPA_SHELL_INDICATORS = [
    'please enable javascript',
    'javascript is disabled',
    # ... 7 more variations
]
MIN_CONTENT_LENGTH = 200
```

### New Method
```python
def _is_spa_shell(self, soup: BeautifulSoup, text_content: str) -> bool:
    """Detect if HTML is just an SPA shell without real content"""
    # Check for JS error messages
    # Check for short content
    # Check for noscript content
    return True/False
```

### Modified Logic in tier1_api_html_json()
```python
# Extract text content from HTML
text_content = soup.get_text(separator='\n', strip=True)

# Check if this is an SPA shell
if self._is_spa_shell(soup, text_content):
    print("[Tier 1] Detected SPA shell - falling back to Tier 2")
    return None  # This allows Tier 2 to run!
```

## Testing

### Unit Tests (8 tests, all passing)
- ✓ Detect "enable javascript" message
- ✓ Detect "javascript is required" message
- ✓ Detect short content
- ✓ Detect large noscript content
- ✓ Valid content NOT flagged as SPA shell
- ✓ Content mentioning "JavaScript" but not as error NOT flagged
- ✓ tier1_api_html_json returns None on SPA shell
- ✓ tier1_api_html_json returns data on valid content

### Manual Test Results
```
Test 1: SPA Shell Detection
✓ SUCCESS: Tier 1 correctly detected SPA shell and returned None
  This allows the scraper to fall back to Tier 2 (Playwright)

Test 2: Valid Content Detection
✓ SUCCESS: Tier 1 correctly scraped valid content
  Title: Character Rankings
  Text length: 254 characters
  Contains expected data: True

Test 3: Complete Scraping Flow
✓ Expected behavior: Tier 1 detected SPA shell, Tier 2 attempted
```

## Security
✓ CodeQL analysis: 0 vulnerabilities found

## Impact
- **Minimal changes**: Only 3 files modified
- **No breaking changes**: API remains the same
- **Improved effectiveness**: Now works correctly with SPA sites
- **Well-tested**: 8 unit tests + manual verification
