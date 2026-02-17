#!/usr/bin/env python3
"""
Test script to verify the scraper's data validation logic.
Tests case-insensitive matching and rejection of invalid data.
"""

import http.server
import socketserver
import threading
import time
from pathlib import Path
from scraper import WebScraper


def start_test_server(port=8893):
    """Start a simple HTTP server for testing"""
    test_dir = Path('/tmp/test_scraper')
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(test_dir), **kwargs)
        
        def log_message(self, format, *args):
            pass  # Suppress logs
    
    httpd = socketserver.TCPServer(('', port), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)
    return httpd


def test_case_insensitive_validation():
    """Test that validation works with different case variations"""
    print("=" * 80)
    print("Test Suite: Data Validation")
    print("=" * 80)
    print()
    
    port = 8893
    httpd = start_test_server(port)
    
    try:
        tests = [
            ("lowercase headers", "yshelper_mock.html", True, "rank, team comp, use rate, own rate, room ratio"),
            ("Mixed Case headers", "mixed_case.html", True, "Rank, Team Comp, Use Rate, Own Rate, Room Ratio"),
            ("UPPERCASE headers", "uppercase.html", True, "RANK, TEAM COMP, USE RATE, OWN RATE, ROOM RATIO"),
            ("No JavaScript error", "no_js.html", False, "Please enable JavaScript message"),
        ]
        
        results = []
        
        for test_name, filename, should_succeed, description in tests:
            print(f"Test: {test_name}")
            print(f"Description: {description}")
            print("-" * 80)
            
            url = f"http://localhost:{port}/{filename}"
            scraper = WebScraper(url, output_dir="/tmp/test_output")
            result = scraper.scrape()
            
            # Check if result matches expectation
            passed = result == should_succeed
            status = "✓ PASS" if passed else "✗ FAIL"
            
            print(f"Expected: {'SUCCESS' if should_succeed else 'FAILURE'}")
            print(f"Actual: {'SUCCESS' if result else 'FAILURE'}")
            print(f"Status: {status}")
            
            if result and scraper.data:
                text_preview = scraper.data.get('text', '')[:100]
                print(f"Data preview: {text_preview}")
            
            print()
            results.append((test_name, passed))
        
        # Print summary
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        
        for test_name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {test_name}")
        
        all_passed = all(passed for _, passed in results)
        print()
        if all_passed:
            print("✓ All tests passed!")
        else:
            print("✗ Some tests failed!")
        
        return all_passed
        
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    import sys
    success = test_case_insensitive_validation()
    sys.exit(0 if success else 1)
