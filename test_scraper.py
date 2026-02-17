#!/usr/bin/env python3
"""
Tests for the web scraper SPA shell detection
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
from scraper import WebScraper


class TestSPAShellDetection(unittest.TestCase):
    """Test cases for SPA shell detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = WebScraper("https://example.com", output_dir="/tmp/test_output")
    
    def test_detect_enable_javascript_message(self):
        """Test detection of 'please enable javascript' message"""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <div>Please enable JavaScript to view this page</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        is_spa = self.scraper._is_spa_shell(soup, text)
        self.assertTrue(is_spa, "Should detect 'enable javascript' message")
    
    def test_detect_javascript_required_message(self):
        """Test detection of 'javascript is required' message"""
        html = """
        <html>
            <head><title>App</title></head>
            <body>
                <p>JavaScript is required to run this application.</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        is_spa = self.scraper._is_spa_shell(soup, text)
        self.assertTrue(is_spa, "Should detect 'javascript is required' message")
    
    def test_detect_short_content(self):
        """Test detection of very short content (likely SPA shell)"""
        html = """
        <html>
            <head><title>App</title></head>
            <body>
                <div id="root"></div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        is_spa = self.scraper._is_spa_shell(soup, text)
        self.assertTrue(is_spa, "Should detect very short content as SPA shell")
    
    def test_detect_large_noscript_content(self):
        """Test detection of significant noscript content"""
        html = """
        <html>
            <head><title>App</title></head>
            <body>
                <noscript>
                    This application requires JavaScript to be enabled.
                    Please enable JavaScript in your browser settings.
                    Without JavaScript, this application will not function properly.
                    For the best experience, please use a modern browser with JavaScript enabled.
                </noscript>
                <div id="app">Loading...</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        is_spa = self.scraper._is_spa_shell(soup, text)
        self.assertTrue(is_spa, "Should detect large noscript content as SPA indicator")
    
    def test_valid_content_not_detected_as_spa_shell(self):
        """Test that valid content with sufficient length is not detected as SPA shell"""
        html = """
        <html>
            <head><title>Real Content Page</title></head>
            <body>
                <h1>Welcome to Our Website</h1>
                <p>This is a real webpage with actual content that users want to see.</p>
                <p>We have multiple paragraphs of meaningful text that provide value.</p>
                <p>This content is not just a placeholder or loading message.</p>
                <ul>
                    <li>Item 1 with description</li>
                    <li>Item 2 with description</li>
                    <li>Item 3 with description</li>
                </ul>
                <p>More content to ensure we exceed the minimum length threshold.</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        is_spa = self.scraper._is_spa_shell(soup, text)
        self.assertFalse(is_spa, "Should not detect valid content as SPA shell")
    
    def test_content_with_javascript_word_but_not_indicator(self):
        """Test that content mentioning JavaScript but not as an error is not flagged"""
        html = """
        <html>
            <head><title>JavaScript Tutorial</title></head>
            <body>
                <h1>Learn JavaScript</h1>
                <p>JavaScript is a powerful programming language used for web development.</p>
                <p>In this tutorial, we'll explore the fundamentals of JavaScript programming.</p>
                <p>We'll cover variables, functions, objects, and more advanced topics.</p>
                <p>By the end of this course, you'll be proficient in JavaScript development.</p>
                <p>The course includes practical examples and hands-on exercises to reinforce learning.</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        is_spa = self.scraper._is_spa_shell(soup, text)
        self.assertFalse(is_spa, "Should not flag content that mentions JavaScript but isn't an error")
    
    @patch('scraper.requests.get')
    def test_tier1_returns_none_on_spa_shell(self, mock_get):
        """Test that tier1_api_html_json returns None when SPA shell is detected"""
        # Mock response with SPA shell
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = """
        <html>
            <head><title>App</title></head>
            <body>
                <div>Please enable JavaScript</div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        result = self.scraper.tier1_api_html_json()
        self.assertIsNone(result, "Should return None when SPA shell is detected")
    
    @patch('scraper.requests.get')
    def test_tier1_returns_data_on_valid_content(self, mock_get):
        """Test that tier1_api_html_json returns data when valid content is found"""
        # Mock response with valid content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = """
        <html>
            <head><title>Valid Page</title></head>
            <body>
                <h1>Welcome</h1>
                <p>This is a real webpage with actual content that users want to see.</p>
                <p>We have multiple paragraphs of meaningful text that provide value.</p>
                <p>This content is not just a placeholder or loading message.</p>
                <p>More content to ensure we exceed the minimum length threshold.</p>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        result = self.scraper.tier1_api_html_json()
        self.assertIsNotNone(result, "Should return data when valid content is found")
        self.assertEqual(result['title'], 'Valid Page')
        self.assertIn('Welcome', result['text'])


if __name__ == '__main__':
    unittest.main()
