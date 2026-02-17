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
    
    # Configuration constants
    DEFAULT_WAIT_TIMEOUT = 3000  # milliseconds
    PLAYWRIGHT_WAIT_UNTIL = 'networkidle'  # Options: 'load', 'domcontentloaded', 'networkidle'
    
    def __init__(self, url: str, output_dir: str = "scraped_data", 
                 wait_timeout: int = None, wait_until: str = None):
        self.url = url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.data = None
        self.wait_timeout = wait_timeout or self.DEFAULT_WAIT_TIMEOUT
        self.wait_until = wait_until or self.PLAYWRIGHT_WAIT_UNTIL
        
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
        Uses JavaScript execution to extract data from dynamically rendered content
        Returns: Data dictionary if successful, None otherwise
        """
        print(f"[Tier 2] Attempting Playwright SPA scraping for {self.url}")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to the page
                print(f"[Tier 2] Loading page with JavaScript enabled...")
                page.goto(self.url, wait_until=self.wait_until, timeout=30000)
                
                # Wait for content to load
                print(f"[Tier 2] Waiting for JavaScript to render content...")
                page.wait_for_timeout(self.wait_timeout)
                
                # Additional wait for any tables or lists that might contain rank data
                try:
                    page.wait_for_selector('table, .table, [class*="rank"], [class*="list"]', timeout=5000)
                    print(f"[Tier 2] Found data container elements")
                except:
                    print(f"[Tier 2] No specific data containers found, using full page content")
                
                # Get page content
                content = page.content()
                title = page.title()
                
                # Get text content
                text_content = page.inner_text('body')
                
                # Use JavaScript to extract data from various sources
                json_data = page.evaluate("""() => {
                    const data = {};
                    
                    // Try to find data in window object
                    if (window.__INITIAL_STATE__) data.initialState = window.__INITIAL_STATE__;
                    if (window.__data) data.windowData = window.__data;
                    if (window.appData) data.appData = window.appData;
                    
                    // Try to find Vue.js data
                    if (window.__NUXT__) data.nuxtData = window.__NUXT__;
                    if (window.$nuxt) {
                        try {
                            data.nuxtState = window.$nuxt.$store?.state;
                        } catch (e) {}
                    }
                    
                    // Try to find React data
                    const reactRoot = document.querySelector('[data-reactroot], #root, #app');
                    if (reactRoot) {
                        const reactProps = Object.keys(reactRoot).find(key => key.startsWith('__react'));
                        if (reactProps) {
                            try {
                                data.reactData = 'React app detected';
                            } catch (e) {}
                        }
                    }
                    
                    // Extract any data attributes from the DOM
                    const dataElements = document.querySelectorAll('[data-rank], [data-ratio], [data-info]');
                    if (dataElements.length > 0) {
                        data.domData = Array.from(dataElements).map(el => ({
                            rank: el.dataset.rank,
                            ratio: el.dataset.ratio,
                            info: el.dataset.info,
                            text: el.innerText?.trim()
                        }));
                    }
                    
                    return Object.keys(data).length > 0 ? data : null;
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
                
                # Sanity check: look for expected patterns like "Rank" and ratio patterns (X:Y:Z)
                has_rank_keyword = 'rank' in text_content.lower()
                has_ratio_pattern = bool(__import__('re').search(r'\d+:\d+:\d+', text_content))
                
                print(f"[Tier 2] Successfully scraped SPA ({len(text_content)} characters)")
                if json_data:
                    print(f"[Tier 2] Extracted JSON data from JavaScript: {list(json_data.keys())}")
                if has_rank_keyword or has_ratio_pattern:
                    print(f"[Tier 2] Sanity check: Found expected data patterns (Rank: {has_rank_keyword}, Ratio: {has_ratio_pattern})")
                
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
