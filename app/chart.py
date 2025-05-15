from playwright.async_api import async_playwright


async def capture_chart(ticker: str, output_path: str):
    url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{ticker}"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)

        # Wait for chart to load
        await page.wait_for_selector('div[data-name="legend"]')

        # Close right sidebar
        await page.locator('button[aria-label="Watchlist, details and news"]').click()

        # Change interval
        await page.keyboard.press("1")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)

        await page.screenshot(path=output_path)
        await browser.close()
