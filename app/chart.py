from playwright.async_api import async_playwright

async def capture_chart(ticker:str, output_path:str):
  url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{ticker}"

  async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(url)
    await page.wait_for_timeout(5000)
    await page.screenshot(path=output_path)
    await browser.close()