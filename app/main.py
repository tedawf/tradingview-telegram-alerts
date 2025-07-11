import asyncio
import logging
import os
import re
from contextlib import asynccontextmanager

import playwright.async_api as pw
from fastapi import FastAPI, Request

from app.chart import capture_chart
from app.settings import settings
from app.telegram import edit_message_with_chart, send_chart, send_message

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)-7s] %(asctime)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.playwright = await pw.async_playwright().start()
    app.state.browser = await app.state.playwright.chromium.launch(headless=True)
    print("[INIT] Playwright and browser launched")

    for _ in range(2):
        asyncio.create_task(chart_worker())

    yield

    print("[SHUTDOWN] Closing browser and playwright")
    await app.state.browser.close()
    await app.state.playwright.stop()


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger(__name__)

chart_task_queue = asyncio.Queue()


HELP_TEXT = """
<b>🤖 <u>Bot Commands:</u></b>

• <code>/show TICKER</code> - Generate chart for any symbol
• <code>/interval MINUTES</code> - Set default timeframe (1/5/15/60/240/1D)
• <code>/theme THEME</code> - Set chart theme (light/dark/system)
• <code>/map TICKER EXCHANGE</code> - Map symbol to exchange
• <code>/unmap TICKER</code> - Remove ticker mapping
• <code>/showmap</code> - Show current symbol mappings
• <code>/help</code> - Show this help

<pre>
Examples:
/show BTCUSD → Generates BTCUSD chart
/interval 60 → Sets 1-hour default timeframe
/theme dark → Sets dark mode as default
/map BTCUSD COINBASE → Maps BTCUSD to Coinbase
/showmap → Shows all ticker mappings
</pre>
"""


@app.post("/command")
async def handle_command(request: Request):
    try:
        data = await request.json()
        logger.info(f"command request: {data}")

        post = data.get("channel_post", {})
        text = post.get("text", "")
        chat_id = post.get("chat", {}).get("id")
        reply_id = post.get("message_id")

        # Only process commands from our channel
        if str(chat_id) != os.getenv("TG_CHANNEL_ID"):
            return {"status": "unauthorized"}

        # Commands
        parts = text.split()
        if not parts or not parts[0].startswith("/"):
            return {"status": "ignored"}

        command = parts[0].lower()
        args = parts[1:]

        if command == "/show" and args:
            return await handle_show_command(app.state.browser, args[0], reply_id)

        elif command == "/interval" and args:
            try:
                int(args[0])  # Validate number
                settings["default_interval"] = args[0]
                return await send_message(
                    f"Default interval set to {args[0]}m", reply_to_msg_id=reply_id
                )
            except ValueError:
                return await send_message("Invalid interval", reply_to_msg_id=reply_id)

        elif command == "/theme" and args:
            theme = args[0].lower()
            if theme in {"light", "dark", "system"}:
                settings["chart_theme"] = theme
                return await send_message(
                    f"Chart theme set to {theme}", reply_to_msg_id=reply_id
                )

        elif command == "/map" and len(args) >= 2:
            settings.set_symbol(args[0], args[1])
            return await send_message(
                f"Mapped {args[0]} to {args[1]}", reply_to_msg_id=reply_id
            )

        elif command == "/unmap" and args:
            if settings.remove_symbol(args[0]):
                return await send_message(
                    f"Removed mapping for {args[0]}", reply_to_msg_id=reply_id
                )
            else:
                return await send_message(
                    f"No mapping found for {args[0]}", reply_to_msg_id=reply_id
                )

        elif command == "/showmap":
            return await handle_showmap_command(reply_id)

        elif command == "/help":
            return await send_message(HELP_TEXT, reply_to_msg_id=reply_id)

        return {"status": "unrecognized command"}

    except Exception as e:
        logging.error(f"Command error: {e}")
        return {"status": "error"}


async def handle_showmap_command(reply_to_id: int):
    try:
        symbol_map = settings["symbol_map"]

        if not symbol_map:
            message = "<b>📊 Symbol Mappings</b>\n\nNo symbols mapped"
        else:
            message = "<b>📊 Symbol Mappings</b>\n\n"
            for ticker, exchange_symbol in symbol_map.items():
                message += f"• <code>{ticker}</code> → <code>{exchange_symbol}</code>\n"

        return await send_message(message, reply_to_msg_id=reply_to_id)

    except Exception as e:
        logger.error(f"Showmap command error: {e}")
        return await send_message(
            "Failed to retrieve symbol mappings", reply_to_msg_id=reply_to_id
        )


async def handle_show_command(browser, ticker: str, reply_to_id: int):
    image_path = f"/tmp/{ticker}_{reply_to_id}.png"
    try:
        await capture_chart(browser, ticker, image_path)
        await send_chart(image_path=image_path, reply_to_msg_id=reply_to_id)
        return {"status": "sent"}
    except Exception as e:
        logger.error(f"Show command error: {e}")
        return await send_message(
            f"Failed to generate {ticker} chart", reply_to_msg_id=reply_to_id
        )


@app.post("/alert")
async def receive_alert(request: Request):
    payload = await request.body()
    logger.info(f"payload: {payload}")
    text = payload.decode()

    # Send to telegram immediately
    response = await send_message(text)
    logger.info(f"Response from sending telegram message: {response}")

    alert_data = _parse_alert_text(text)
    if not alert_data:
        return {"status": "invalid format"}

    ticker = alert_data["ticker"]
    logger.info(f"Starting capture chart task for {ticker}")
    await chart_task_queue.put((ticker, response["message_id"], text))

    return {"status": "sent"}


def _parse_alert_text(text: str):
    match = re.match(r"([\w./:-]+) Crossing ([\d.]+)", text)
    if match:
        return {"ticker": match.group(1), "value": float(match.group(2))}
    return None


async def chart_worker():
    browser = app.state.browser
    while True:
        task = await chart_task_queue.get()
        ticker, message_id, caption = task
        try:
            logger.info(f"[WORKER] Processing chart for {ticker}")
            image_path = f"/tmp/{ticker}_{message_id}.png"
            await capture_chart(browser, ticker, image_path)
            await edit_message_with_chart(message_id, image_path, caption)
            await asyncio.sleep(1.0)  # throttle between tasks
        except Exception as e:
            logger.error(f"[WORKER] Chart error for {ticker}: {e}")
        finally:
            chart_task_queue.task_done()
