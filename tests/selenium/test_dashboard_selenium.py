"""
End-to-end tests with Selenium - the same dashboard flows as the Playwright
suite, written with Selenium WebDriver.

Why both? The JD names Selenium AND Playwright. Testing the same UI two ways
demonstrates the concepts transfer across tools, and lets you speak to the
practical differences:
  - Playwright has built-in auto-waiting; Selenium needs explicit waits
    (WebDriverWait) for async updates.
  - Selenium is older/more established; Playwright is newer with a simpler API.

Requires the app running at http://localhost:8000 and a Chrome/Chromedriver.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


def test_dashboard_title(driver):
    driver.get(f"{BASE_URL}/dashboard")
    title = driver.find_element(By.ID, "title")
    assert title.text == "ESS Site Monitor"


def test_valid_reading_selenium(driver):
    driver.get(f"{BASE_URL}/dashboard")
    driver.find_element(By.ID, "voltage-input").send_keys("400")
    driver.find_element(By.ID, "temp-input").send_keys("25")
    driver.find_element(By.ID, "soc-input").send_keys("80")
    driver.find_element(By.ID, "submit-btn").click()
    # Selenium needs an explicit wait for the async fetch (unlike Playwright)
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.ID, "result"), "Reading saved")
    )


def test_invalid_reading_selenium(driver):
    driver.get(f"{BASE_URL}/dashboard")
    driver.find_element(By.ID, "voltage-input").send_keys("5000")
    driver.find_element(By.ID, "temp-input").send_keys("25")
    driver.find_element(By.ID, "soc-input").send_keys("80")
    driver.find_element(By.ID, "submit-btn").click()
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.ID, "result"), "Invalid reading")
    )
