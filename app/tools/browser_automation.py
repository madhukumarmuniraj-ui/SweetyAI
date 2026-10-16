"""
SweetyAI Browser Automation Tools
Web scraping, form filling, and browser control using Playwright
"""

import os
import time
from typing import Dict, List, Optional, Any
import json
import asyncio

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("[Browser Tools] Playwright not available. Run: pip install playwright && playwright install")


class BrowserAutomation:
    """Browser automation wrapper using Playwright."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self, headless: bool = True, browser_type: str = "chromium") -> str:
        """Start a browser instance."""
        if not PLAYWRIGHT_AVAILABLE:
            return "Error: Playwright not installed"

        try:
            self.playwright = sync_playwright().start()

            if browser_type == "firefox":
                self.browser = self.playwright.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                self.browser = self.playwright.webkit.launch(headless=headless)
            else:
                self.browser = self.playwright.chromium.launch(headless=headless)

            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = self.context.new_page()

            return f"Browser started ({browser_type}, headless={headless})"
        except Exception as e:
            return f"Error starting browser: {e}"

    def close_browser(self) -> str:
        """Close the browser."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            return "Browser closed"
        except Exception as e:
            return f"Error closing browser: {e}"

    def navigate(self, url: str, wait_until: str = "networkidle") -> str:
        """Navigate to a URL."""
        if not self.page:
            return "Error: Browser not started"

        try:
            self.page.goto(url, wait_until=wait_until)
            return f"Navigated to: {url}"
        except Exception as e:
            return f"Error navigating: {e}"

    def screenshot(self, output_path: str, full_page: bool = False) -> str:
        """Take a screenshot."""
        if not self.page:
            return "Error: Browser not started"

        try:
            self.page.screenshot(path=output_path, full_page=full_page)
            return f"Screenshot saved: {output_path}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

    def get_page_content(self) -> str:
        """Get the page HTML content."""
        if not self.page:
            return "Error: Browser not started"

        try:
            return self.page.content()
        except Exception as e:
            return f"Error getting content: {e}"

    def get_text(self, selector: Optional[str] = None) -> str:
        """Extract text from page or specific element."""
        if not self.page:
            return "Error: Browser not started"

        try:
            if selector:
                element = self.page.query_selector(selector)
                if element:
                    return element.inner_text()
                return f"Element not found: {selector}"
            else:
                return self.page.inner_text('body')
        except Exception as e:
            return f"Error extracting text: {e}"

    def click_element(self, selector: str) -> str:
        """Click an element."""
        if not self.page:
            return "Error: Browser not started"

        try:
            self.page.click(selector)
            return f"Clicked: {selector}"
        except Exception as e:
            return f"Error clicking element: {e}"

    def fill_form(self, selector: str, value: str) -> str:
        """Fill a form field."""
        if not self.page:
            return "Error: Browser not started"

        try:
            self.page.fill(selector, value)
            return f"Filled {selector} with: {value}"
        except Exception as e:
            return f"Error filling form: {e}"

    def wait_for_selector(self, selector: str, timeout: int = 30000) -> str:
        """Wait for an element to appear."""
        if not self.page:
            return "Error: Browser not started"

        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return f"Element found: {selector}"
        except Exception as e:
            return f"Timeout waiting for: {selector}"

    def scrape_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Scrape data using CSS selectors."""
        if not self.page:
            return {"error": "Browser not started"}

        try:
            results = {}
            for key, selector in selectors.items():
                try:
                    elements = self.page.query_selector_all(selector)
                    if len(elements) == 1:
                        results[key] = elements[0].inner_text()
                    elif len(elements) > 1:
                        results[key] = [el.inner_text() for el in elements]
                    else:
                        results[key] = None
                except:
                    results[key] = None

            return results
        except Exception as e:
            return {"error": str(e)}


# Global browser instance
_browser_instance = None


def get_browser() -> BrowserAutomation:
    """Get or create browser automation instance."""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserAutomation()
    return _browser_instance


# Standalone wrapper functions matching the tool registry imports

def browse_url(url: str, extract_text: bool = True) -> str:
    """Browse a URL and optionally extract text."""
    if not PLAYWRIGHT_AVAILABLE:
        return "Error: Playwright not installed. Run: pip install playwright && playwright install"

    browser = get_browser()
    if not browser.page:
        start_result = browser.start_browser(headless=True)
        if "Error" in start_result:
            return start_result

    nav_result = browser.navigate(url)
    if "Error" in nav_result:
        return nav_result

    if extract_text:
        time.sleep(2)
        return browser.get_text()

    return f"Successfully loaded: {url}"


def navigate_to_url(url: str, extract_text: bool = True) -> str:
    """Standalone wrapper for browser navigation."""
    return browse_url(url, extract_text=extract_text)


def click_element(selector: str) -> str:
    """Click an element using the global browser instance."""
    browser = get_browser()
    if not browser.page:
        return "Error: Browser not started"
    return browser.click_element(selector)


def fill_form_field(selector: str, value: str) -> str:
    """Fill a form field using the global browser instance."""
    browser = get_browser()
    if not browser.page:
        return "Error: Browser not started"
    return browser.fill_form(selector, value)


def take_screenshot(output_path: str = "screenshot.png", full_page: bool = True) -> str:
    """Take a screenshot using the global browser instance."""
    browser = get_browser()
    if not browser.page:
        return "Error: Browser not started"
    return browser.screenshot(output_path, full_page=full_page)


def extract_text(selector: Optional[str] = None) -> str:
    """Extract text using the global browser instance."""
    browser = get_browser()
    if not browser.page:
        return "Error: Browser not started"
    return browser.get_text(selector)


def web_scrape(url: str, selectors: Dict[str, str]) -> str:
    """Scrape specific data from a webpage."""
    if not PLAYWRIGHT_AVAILABLE:
        return "Error: Playwright not installed"

    browser = get_browser()
    if not browser.page:
        browser.start_browser(headless=True)

    browser.navigate(url)
    time.sleep(2)

    data = browser.scrape_data(selectors)
    return json.dumps(data, indent=2, ensure_ascii=False)


def fill_web_form(url: str, form_data: Dict[str, str], submit_selector: Optional[str] = None) -> str:
    """Fill and submit a web form."""
    if not PLAYWRIGHT_AVAILABLE:
        return "Error: Playwright not installed"

    browser = get_browser()
    if not browser.page:
        browser.start_browser(headless=False)

    browser.navigate(url)
    time.sleep(1)

    results = []
    for selector, value in form_data.items():
        result = browser.fill_form(selector, value)
        results.append(result)

    if submit_selector:
        browser.click_element(submit_selector)
        results.append(f"Clicked submit button: {submit_selector}")

    return "\n".join(results)


def close_browser_session() -> str:
    """Close the browser session."""
    global _browser_instance
    if _browser_instance:
        result = _browser_instance.close_browser()
        _browser_instance = None
        return result
    return "No browser session active"


__all__ = [
    'BrowserAutomation', 'get_browser',
    'browse_url', 'web_scrape', 'fill_web_form',
    'take_website_screenshot', 'close_browser_session',
    'navigate_to_url', 'click_element', 'fill_form_field',
    'take_screenshot', 'extract_text'
]