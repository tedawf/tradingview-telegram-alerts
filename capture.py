import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import telegrambot


def setup() -> webdriver.Chrome:
    print(f"setup selenium start: {str(datetime.now())}")

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,720")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_page_load_timeout(20)
    print(f"setup selenium completed: {str(datetime.now())}")

    return driver


async def screenshot(driver: webdriver.Chrome, chart, ticker, adjustment):
    chart_url = f"https://www.tradingview.com/chart/{chart}/?symbol={ticker}"
    print(f"chart_url: {chart_url}")

    print(f"opening chart {chart}: {str(datetime.now())}")
    driver.get(chart_url)
    print(f"page loaded: {str(datetime.now())}")

    print(f"closing sidebar: {str(datetime.now())}")
    WebDriverWait(driver, 30).until(
        ec.element_to_be_clickable(
            (By.XPATH, "//button[@aria-label='Watchlist, details and news']")
        )
    ).click()

    print(f"adjusting position by {adjustment}: {str(datetime.now())}")
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    actions.send_keys(Keys.RIGHT * adjustment).perform()

    print(f"chart is ready for capture: {str(datetime.now())}")
    WebDriverWait(driver, 30).until(
        ec.invisibility_of_element_located(
            (By.XPATH, "//span[@class='loader-l31H9iuA blockHidden-e6PF69Df']")
        )
    )
    print(f"chart fully loaded: {str(datetime.now())}")

    screenshot_file = "ss.png"
    if driver.get_screenshot_as_file(screenshot_file):
        return screenshot_file
    else:
        return None


def quit_browser(driver: webdriver.Chrome, screenshot_file):
    print(f"quit browser : {str(datetime.now())}")
    driver.quit()
    os.remove(screenshot_file)


async def send_chart(chart, ticker, message, delivery, adjustment):
    print(f"message: {message}")
    if delivery == "asap":
        await telegrambot.send_message(message)

    driver = setup()
    screenshot_file = await screenshot(driver, chart, ticker, adjustment)
    print(f"screenshot_file: {screenshot_file}")

    if delivery != "asap":
        await telegrambot.send_image(screenshot_file, message)
        quit_browser(driver, screenshot_file)
        return

    quit_browser(driver, screenshot_file)
    await telegrambot.send_image(screenshot_file)


async def send_chart_async(chart_url, ticker, message, delivery, adjustment):
    await send_chart(chart_url, ticker, message, delivery, adjustment)
