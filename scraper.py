#!/usr/bin/env python3
"""
Web scraper with tiered approach:
1. Try API/HTML/JSON
2. If failed, try SPA with Playwright
3. If failed, use visual AI (placeholder)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup


class WebScraper:
    """Main web scraper class with tiered scraping strategies"""
    
    def __init__(self, url: str, output_dir: str = "scraped_data"):
        self.url = url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.data = None
        
    def tier1_api_html_json(self) -> Optional[Dict[str, Any]]:
        """
        Tier 1: Try to scrape using API/HTML/JSON endpoints
        Returns: Data dictionary if successful, None otherwise
        """
        print(f"[Tier 1] Attempting API/HTML/JSON scraping for {self.url}")
        
        try:
            # Try to fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check if response is JSON
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                print("[Tier 1] Response is JSON")
                return response.json()
            
            # Try to parse as HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for embedded JSON in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('window.__INITIAL_STATE__' in script.string or 
                                     'window.__data' in script.string or
                                     '{' in script.string):
                    try:
                        # Try to extract JSON from script
                        script_text = script.string.strip()
                        # Look for JSON patterns
                        if '=' in script_text:
                            json_start = script_text.find('{')
                            json_end = script_text.rfind('}') + 1
                            if json_start != -1 and json_end > json_start:
                                json_str = script_text[json_start:json_end]
                                data = json.loads(json_str)
                                print(f"[Tier 1] Found embedded JSON in script tag")
                                return data
                    except (json.JSONDecodeError, ValueError):
                        continue
            
            # Extract text content from HTML
            data = {
                'url': self.url,
                'title': soup.title.string if soup.title else 'No title',
                'text': soup.get_text(separator='\n', strip=True),
                'scraped_at': datetime.now().isoformat()
            }
            
            print(f"[Tier 1] Scraped HTML content ({len(data['text'])} characters)")
            return data
            
        except Exception as e:
            print(f"[Tier 1] Failed: {str(e)}")
            return None
    
    def tier2_playwright_spa(self) -> Optional[Dict[str, Any]]:
        """
        Tier 2: Use Playwright for SPA (Single Page Application) scraping
        Returns: Data dictionary if successful, None otherwise
        """
        print(f"[Tier 2] Attempting Playwright SPA scraping for {self.url}")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to the page
                print(f"[Tier 2] Loading page...")
                page.goto(self.url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load (adjust selector as needed)
                page.wait_for_timeout(3000)  # Wait 3 seconds for dynamic content
                
                # Get page content
                content = page.content()
                title = page.title()
                
                # Get text content
                text_content = page.inner_text('body')
                
                # Try to get any JSON data from the page
                json_data = page.evaluate("""() => {
                    // Try to find data in window object
                    if (window.__INITIAL_STATE__) return window.__INITIAL_STATE__;
                    if (window.__data) return window.__data;
                    if (window.appData) return window.appData;
                    return null;
                }""")
                
                browser.close()
                
                data = {
                    'url': self.url,
                    'title': title,
                    'text': text_content,
                    'html': content,
                    'json_data': json_data,
                    'scraped_at': datetime.now().isoformat()
                }
                
                print(f"[Tier 2] Successfully scraped SPA ({len(text_content)} characters)")
                return data
                
        except ImportError:
            print("[Tier 2] Playwright not installed. Install with: playwright install chromium")
            return None
        except Exception as e:
            print(f"[Tier 2] Failed: {str(e)}")
            return None
    
    def tier3_visual_ai(self) -> Optional[Dict[str, Any]]:
        """
        Tier 3: Visual AI scraping (placeholder for future implementation)
        Returns: Data dictionary if successful, None otherwise
        """
        print(f"[Tier 3] Visual AI scraping not yet implemented")
        print("[Tier 3] This would use computer vision and OCR to extract data from screenshots")
        return None
    
    def scrape(self) -> bool:
        """
        Execute tiered scraping strategy
        Returns: True if successful, False otherwise
        """
        # Try Tier 1
        self.data = self.tier1_api_html_json()
        if self.data:
            print("✓ Successfully scraped using Tier 1 (API/HTML/JSON)")
            return True
        
        # Try Tier 2
        self.data = self.tier2_playwright_spa()
        if self.data:
            print("✓ Successfully scraped using Tier 2 (Playwright SPA)")
            return True
        
        # Try Tier 3
        self.data = self.tier3_visual_ai()
        if self.data:
            print("✓ Successfully scraped using Tier 3 (Visual AI)")
            return True
        
        print("✗ All scraping tiers failed")
        return False
    
    def save_to_file(self, filename: Optional[str] = None) -> str:
        """
        Save scraped data to text files
        Returns: Path to saved file
        """
        if not self.data:
            raise ValueError("No data to save. Run scrape() first.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if filename is None:
            filename = f"scraped_data_{timestamp}"
        
        # Save as text file
        text_file = self.output_dir / f"{filename}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"URL: {self.data.get('url', 'N/A')}\n")
            f.write(f"Title: {self.data.get('title', 'N/A')}\n")
            f.write(f"Scraped at: {self.data.get('scraped_at', 'N/A')}\n")
            f.write("-" * 80 + "\n\n")
            f.write(self.data.get('text', 'No text content'))
        
        # Save as JSON file for structured data
        json_file = self.output_dir / f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to:")
        print(f"  - {text_file}")
        print(f"  - {json_file}")
        
        return str(text_file)


def main():
    """Main function"""
    # Default URL from the problem statement
    url = "https://app.yshelper.com/#/pages/rank2/rank2"
    
    # Allow URL to be passed as command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    print("=" * 80)
    print("Web Scraper - Tiered Approach")
    print("=" * 80)
    print(f"Target URL: {url}")
    print()
    
    # Create scraper instance
    scraper = WebScraper(url)
    
    # Execute scraping
    if scraper.scrape():
        # Save data to files
        scraper.save_to_file()
        print()
        print("=" * 80)
        print("Scraping completed successfully!")
        print("=" * 80)
        return 0
    else:
        print()
        print("=" * 80)
        print("Scraping failed!")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
