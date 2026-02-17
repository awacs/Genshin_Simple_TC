#!/usr/bin/env python3
"""
Example usage for scraping https://app.yshelper.com/#/pages/rank2/rank2

This script demonstrates how to use the scraper for the target website.
Since the website appears to be a Single Page Application (SPA), 
the scraper will likely use Tier 2 (Playwright) to scrape it.
"""

from scraper import WebScraper


def scrape_yshelper():
    """
    Scrape the yshelper rank page
    """
    url = "https://app.yshelper.com/#/pages/rank2/rank2"
    
    print("Scraping yshelper.com rank page...")
    print(f"URL: {url}")
    print()
    
    # Create scraper instance
    scraper = WebScraper(url, output_dir="scraped_data")
    
    # Execute tiered scraping
    if scraper.scrape():
        # Save to file
        output_file = scraper.save_to_file("yshelper_rank_data")
        print()
        print(f"Success! Data saved to: {output_file}")
        
        # Print summary
        if scraper.data:
            print()
            print("Data summary:")
            print(f"  - Title: {scraper.data.get('title', 'N/A')}")
            print(f"  - Text length: {len(scraper.data.get('text', ''))} characters")
            if scraper.data.get('json_data'):
                print(f"  - Embedded JSON data: Found")
            print()
            print("Preview (first 500 characters):")
            print("-" * 80)
            print(scraper.data.get('text', '')[:500])
            print("-" * 80)
        
        return True
    else:
        print()
        print("Failed to scrape the website.")
        print()
        print("Possible reasons:")
        print("  - The website is not accessible from this network")
        print("  - The website requires authentication")
        print("  - The website has anti-scraping measures")
        print()
        print("Try the following:")
        print("  1. Check if the website is accessible in a browser")
        print("  2. Ensure all dependencies are installed (pip install -r requirements.txt)")
        print("  3. Install Playwright browsers (playwright install chromium)")
        
        return False


if __name__ == "__main__":
    scrape_yshelper()
