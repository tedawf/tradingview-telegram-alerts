import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")


async def send_message(text: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json={"chat_id": TG_CHANNEL_ID, "text": text})

    return res.json()["result"]


async def edit_message_with_chart(message_id: int, image_path: str, caption: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/editMessageMedia"
    media = {"type": "photo", "media": "attach://photo", "caption": caption}

    async with httpx.AsyncClient() as client:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {
                "chat_id": TG_CHANNEL_ID,
                "message_id": message_id,
                "media": json.dumps(media),
            }

            res = await client.post(url, data=data, files=files)
            res.raise_for_status()
            return res.json()
