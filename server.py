import os
import urllib.parse
import dotenv

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import capture
import telegrambot


class Alert(BaseModel):
    message: str
    exchange: str
    ticker: str
    delivery: str | str = "asap"
    adjustment: int | int = 1000


app = FastAPI()


@app.get("/")
async def read_root():
    return "ivan bot is alive!"


@app.post("/alert")
async def alert(alert: Alert | str, chart: str | None = None):
    if isinstance(alert, str):
        print("received text")
        await telegrambot.send_message(message=alert)
    else:
        print("received json")
        ticker = urllib.parse.quote(f"{alert.exchange}:{alert.ticker}")
        await capture.send_chart_async(
            chart_url=chart,
            ticker=ticker,
            message=alert.message,
            delivery=alert.delivery,
            adjustment=alert.adjustment,
        )
    return "ok"


def start():
    dotenv.load_dotenv(override=True)
    uvicorn.run(app=app, host="0.0.0.0", port=int(os.environ.get("PORT")))
