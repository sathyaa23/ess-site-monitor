"""
End-to-end tests with Playwright - drive a real browser against the running app.

These are the fewest, slowest tests (top of the pyramid) but they verify the
whole system as a user experiences it: UI -> API -> validation -> UI feedback.

Requires the app to be running at http://localhost:8000 (the CI workflow
starts it before running these).
"""

import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


def test_dashboard_loads(browser_page):
    browser_page.goto(f"{BASE_URL}/dashboard")
    expect(browser_page.locator("#title")).to_have_text("ESS Site Monitor")


def test_valid_reading_shows_success(browser_page):
    page = browser_page
    page.goto(f"{BASE_URL}/dashboard")
    page.fill("#voltage-input", "400")
    page.fill("#temp-input", "25")
    page.fill("#soc-input", "80")
    page.click("#submit-btn")
    # wait for the async fetch to update the result div
    expect(page.locator("#result")).to_contain_text("Reading saved")


def test_invalid_reading_shows_error(browser_page):
    page = browser_page
    page.goto(f"{BASE_URL}/dashboard")
    page.fill("#voltage-input", "5000")   # out of range
    page.fill("#temp-input", "25")
    page.fill("#soc-input", "80")
    page.click("#submit-btn")
    expect(page.locator("#result")).to_contain_text("Invalid reading")
    expect(page.locator("#result")).to_contain_text("voltage")
