import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")


async def send_message(text: str, reply_to_msg_id: int = None):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    body = {
        "chat_id": TG_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_to_msg_id:
        body["reply_to_message_id"] = reply_to_msg_id

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=body)
        res.raise_for_status()
    return res.json().get("result", {})


async def edit_message_with_chart(message_id: int, image_path: str, caption: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/editMessageMedia"
    media = {
        "type": "photo",
        "media": "attach://photo",
        "caption": caption,
        "parse_mode": "HTML",
    }
    data = {
        "chat_id": TG_CHANNEL_ID,
        "message_id": message_id,
        "media": json.dumps(media),
    }

    async with httpx.AsyncClient() as client:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            res = await client.post(url, data=data, files=files)
            res.raise_for_status()


async def send_chart(image_path: str, reply_to_msg_id: int = None):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    data = {"chat_id": TG_CHANNEL_ID}
    if reply_to_msg_id:
        data["reply_to_message_id"] = reply_to_msg_id

    async with httpx.AsyncClient() as client:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            res = await client.post(url, data=data, files=files)
            res.raise_for_status()
        return res.json().get("result", {})
