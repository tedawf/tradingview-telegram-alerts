import logging
import re

from playwright.async_api import async_playwright

from app.settings import settings

logger = logging.getLogger(__name__)


async def capture_chart(ticker: str, output_path: str):
    settings.load()

    # Prefer mapped
    mapped = settings.get_symbol(ticker)
    if mapped:
        symbol = mapped

    # Else prefer TWSE for digits only
    elif re.fullmatch(r"\d+", ticker):
        symbol = f"TWSE:{ticker}"

    # Let TV do the routing
    else:
        symbol = ticker

    interval = settings["default_interval"]
    theme = settings["chart_theme"]

    url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
    if theme == "dark":
        url += "&theme=dark"
    logger.info(f"url: {url}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(url, timeout=10000)

        # Wait for chart to load
        # await page.wait_for_selector('div[data-name="legend"]', timeout=5000)
        await page.wait_for_selector("canvas", timeout=5000)

        # Close right sidebar
        try:
            await page.locator(
                'button[aria-label="Watchlist, details and news"]'
            ).click()
        except:
            logger.error("sidebar button not found")

        await page.screenshot(path=output_path)
        await browser.close()
