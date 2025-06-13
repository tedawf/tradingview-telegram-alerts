import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)-7s] %(asctime)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
import re

from fastapi import BackgroundTasks, FastAPI, Request

from app.chart import capture_chart
from app.telegram import edit_message_with_chart, send_message

app = FastAPI()
logger = logging.getLogger(__name__)


@app.post("/alert")
async def receive_alert(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    logger.info(f"payload: {payload}")
    text = payload.decode()

    # Send to telegram immediately
    response = await send_message(text)
    logger.info(f"Response from sending telegram message: {response}")

    alert_data = _parse_alert_text(text)
    if not alert_data:
        return {"status": "invalid format"}

    logger.info(f"Starting capture chart task with alert data: {alert_data}")
    background_tasks.add_task(
        capture_chart_task, alert_data, response["message_id"], text
    )

    return {"status": "sent"}


def _parse_alert_text(text: str):
    match = re.match(r"([\w./:-]+) Crossing ([\d.]+)", text)
    if match:
        return {"ticker": match.group(1), "value": float(match.group(2))}
    return None


async def capture_chart_task(alert_data: dict, message_id: int, caption: str):
    ticker = alert_data["ticker"]
    image_path = f"/tmp/{ticker}.png"

    try:
        await capture_chart(ticker, image_path)
        await edit_message_with_chart(message_id, image_path, caption)
    except Exception as e:
        print(f"Error while capturing chart: {e}")
