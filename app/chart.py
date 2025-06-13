import logging

from playwright.async_api import async_playwright

from app.settings import settings

logger = logging.getLogger(__name__)


async def capture_chart(ticker: str, output_path: str):
    settings.load()

    # Use mapping if exists, otherwise use ticker directly
    mapped_ticker = settings.get_symbol(ticker) or ticker
    interval = settings["default_interval"]
    theme = settings["chart_theme"]

    url = (
        f"https://www.tradingview.com/chart/?symbol={mapped_ticker}&interval={interval}"
    )
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
