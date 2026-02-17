#!/usr/bin/env python3
"""
Demo script to test the scraper with local HTML file
This demonstrates all tiers of the scraping functionality
"""

import json
import os
from pathlib import Path
from scraper import WebScraper


def create_test_html():
    """Create a test HTML file to scrape"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Rank Page</title>
        <script>
            window.__INITIAL_STATE__ = {
                "ranks": [
                    {"rank": 1, "name": "Player A", "score": 9500},
                    {"rank": 2, "name": "Player B", "score": 9200},
                    {"rank": 3, "name": "Player C", "score": 8900}
                ],
                "updated": "2024-01-01"
            };
        </script>
    </head>
    <body>
        <h1>Rank Data</h1>
        <div class="rank-list">
            <div>Rank 1: Player A - 9500 points</div>
            <div>Rank 2: Player B - 9200 points</div>
            <div>Rank 3: Player C - 8900 points</div>
        </div>
    </body>
    </html>
    """
    
    html_file = test_dir / "test_rank.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    return html_file


def test_tier1():
    """Test Tier 1 scraping with local HTML file"""
    print("=" * 80)
    print("Testing Tier 1: API/HTML/JSON Scraping")
    print("=" * 80)
    
    html_file = create_test_html()
    file_url = f"file://{html_file.absolute()}"
    
    scraper = WebScraper(file_url, output_dir="test_output")
    
    # Manually test tier1 method
    data = scraper.tier1_api_html_json()
    
    if data:
        print("\n✓ Tier 1 scraping successful!")
        print(f"\nExtracted data preview:")
        print(f"  Title: {data.get('title', 'N/A')}")
        print(f"  Text length: {len(data.get('text', ''))} characters")
        print(f"\nFirst 200 characters of text:")
        print(data.get('text', '')[:200])
        
        # Save the data
        scraper.data = data
        scraper.save_to_file("tier1_demo")
        return True
    else:
        print("\n✗ Tier 1 scraping failed")
        return False


def test_tier2():
    """Test Tier 2 scraping with local HTML file"""
    print("\n" + "=" * 80)
    print("Testing Tier 2: Playwright SPA Scraping")
    print("=" * 80)
    
    html_file = create_test_html()
    file_url = f"file://{html_file.absolute()}"
    
    scraper = WebScraper(file_url, output_dir="test_output")
    
    # Manually test tier2 method
    data = scraper.tier2_playwright_spa()
    
    if data:
        print("\n✓ Tier 2 scraping successful!")
        print(f"\nExtracted data preview:")
        print(f"  Title: {data.get('title', 'N/A')}")
        print(f"  Text length: {len(data.get('text', ''))} characters")
        print(f"  JSON data found: {data.get('json_data') is not None}")
        
        if data.get('json_data'):
            print(f"\nExtracted JSON data:")
            print(json.dumps(data['json_data'], indent=2))
        
        # Save the data
        scraper.data = data
        scraper.save_to_file("tier2_demo")
        return True
    else:
        print("\n✗ Tier 2 scraping failed")
        return False


def main():
    """Main demo function"""
    print("Web Scraper Demo - Testing Tiered Approach")
    print()
    
    # Test Tier 1
    tier1_success = test_tier1()
    
    # Test Tier 2
    tier2_success = test_tier2()
    
    print("\n" + "=" * 80)
    print("Demo Summary")
    print("=" * 80)
    print(f"Tier 1 (API/HTML/JSON): {'✓ PASSED' if tier1_success else '✗ FAILED'}")
    print(f"Tier 2 (Playwright SPA): {'✓ PASSED' if tier2_success else '✗ FAILED'}")
    print(f"Tier 3 (Visual AI): Not implemented (placeholder)")
    print()
    print("Check the 'test_output/' directory for scraped data files")
    print("=" * 80)


if __name__ == "__main__":
    main()
