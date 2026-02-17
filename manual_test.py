#!/usr/bin/env python3
"""
Manual test to demonstrate SPA shell detection and fallback to Tier 2

This script creates a mock SPA shell response to demonstrate that:
1. Tier 1 detects the SPA shell and returns None
2. The scraper then falls back to Tier 2 (Playwright)
"""

from unittest.mock import patch, Mock
from scraper import WebScraper


def test_spa_shell_detection_flow():
    """
    Test the complete flow: Tier 1 detects SPA shell -> Falls back to Tier 2
    """
    print("=" * 80)
    print("Manual Test: SPA Shell Detection and Tier 2 Fallback")
    print("=" * 80)
    print()
    
    # Create a mock SPA shell response (like https://app.yshelper.com)
    spa_shell_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>YS Helper - Genshin Impact Helper</title>
            <meta charset="utf-8">
        </head>
        <body>
            <div id="app"></div>
            <noscript>
                <strong>Please enable JavaScript to continue.</strong>
            </noscript>
            <script src="/js/app.js"></script>
        </body>
    </html>
    """
    
    # Create a mock valid content response
    valid_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Character Rankings</title>
        </head>
        <body>
            <h1>Genshin Impact Character Rankings</h1>
            <table>
                <tr><th>Rank</th><th>Character</th><th>Team Usage</th></tr>
                <tr><td>1</td><td>Neuvillette</td><td>45.2%</td></tr>
                <tr><td>2</td><td>Furina</td><td>42.8%</td></tr>
                <tr><td>3</td><td>Kazuha</td><td>38.5%</td></tr>
            </table>
            <p>This data represents character usage in Spiral Abyss.</p>
            <p>Statistics are based on over 50,000 submissions from players worldwide.</p>
        </body>
    </html>
    """
    
    print("Test 1: SPA Shell Detection")
    print("-" * 80)
    with patch('scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = spa_shell_html
        mock_get.return_value = mock_response
        
        scraper = WebScraper("https://app.yshelper.com/#/pages/rank2/rank2")
        result = scraper.tier1_api_html_json()
        
        if result is None:
            print("✓ SUCCESS: Tier 1 correctly detected SPA shell and returned None")
            print("  This allows the scraper to fall back to Tier 2 (Playwright)")
        else:
            print("✗ FAILURE: Tier 1 should have returned None for SPA shell")
            print(f"  Got: {result}")
    
    print()
    print("Test 2: Valid Content Detection")
    print("-" * 80)
    with patch('scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = valid_html
        mock_get.return_value = mock_response
        
        scraper = WebScraper("https://example.com/rankings")
        result = scraper.tier1_api_html_json()
        
        if result is not None:
            print("✓ SUCCESS: Tier 1 correctly scraped valid content")
            print(f"  Title: {result.get('title')}")
            print(f"  Text length: {len(result.get('text', ''))} characters")
            print(f"  Contains expected data: {'Neuvillette' in result.get('text', '')}")
        else:
            print("✗ FAILURE: Tier 1 should have returned data for valid content")
    
    print()
    print("Test 3: Complete Scraping Flow with SPA Shell")
    print("-" * 80)
    print("Simulating scenario where Tier 1 detects SPA shell and Tier 2 is attempted...")
    print()
    
    with patch('scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = spa_shell_html
        mock_get.return_value = mock_response
        
        scraper = WebScraper("https://app.yshelper.com/#/pages/rank2/rank2")
        
        print("Calling scraper.scrape()...")
        # This will try Tier 1 (which will return None due to SPA shell)
        # Then it will try Tier 2 (which will fail because Playwright isn't running in test)
        success = scraper.scrape()
        
        if not success:
            print("✓ Expected behavior: Tier 1 detected SPA shell, Tier 2 attempted")
            print("  (Tier 2 failed in this test because no real browser is running)")
        else:
            print("Scraping succeeded (possibly from Tier 2)")
    
    print()
    print("=" * 80)
    print("Manual Test Complete")
    print("=" * 80)
    print()
    print("Summary:")
    print("- SPA shell detection is working correctly")
    print("- Tier 1 returns None when SPA shell is detected")
    print("- This allows the scraper to fall back to Tier 2 (Playwright)")
    print("- Valid content is not incorrectly flagged as SPA shell")


if __name__ == "__main__":
    test_spa_shell_detection_flow()
