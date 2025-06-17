import logging
import re

from playwright.async_api import Browser

from app.settings import settings

logger = logging.getLogger(__name__)


async def capture_chart(browser: Browser, ticker: str, output_path: str):
    settings.load()

    # Prefer mapped > TWSE (digits) > TV
    mapped = settings.get_symbol(ticker)
    if mapped:
        symbol = mapped
    elif re.fullmatch(r"\d+", ticker):
        symbol = f"TWSE:{ticker}"
    else:
        symbol = ticker

    interval = settings["default_interval"]
    theme = settings["chart_theme"]

    url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
    if theme == "dark":
        url += "&theme=dark"
    logger.info(f"url: {url}")

    # Playwright
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(url, timeout=20000)

        # Wait for chart to load
        await page.wait_for_selector("canvas", timeout=10000)

        # Close right sidebar
        try:
            await page.locator(
                'button[aria-label="Watchlist, details and news"]'
            ).click()
        except:
            logger.error("sidebar button not found")

        await page.screenshot(path=output_path)

    finally:
        await context.close()
