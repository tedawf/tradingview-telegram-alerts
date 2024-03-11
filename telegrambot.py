import os

from telegram import Bot


async def send_message(message):
    tg_bot = Bot(token=os.environ.get("TOKEN"))
    channel_id = os.environ.get("CHANNEL_ID")
    try:
        await tg_bot.send_message(
            text=message,
            chat_id=channel_id,
            parse_mode="MARKDOWN",
        )
        return True
    except KeyError:
        await tg_bot.send_message(
            text=message,
            chat_id=channel_id,
            parse_mode="MARKDOWN",
        )
    except Exception as e:
        print("Error:\n>", e)
    return False


async def send_image(image_path, caption=None):
    tg_bot = Bot(token=os.environ.get("TOKEN"))
    channel_id = os.environ.get("CHANNEL_ID")

    if caption:
        await tg_bot.send_photo(
            chat_id=channel_id, photo=open(image_path, "rb"), caption=caption
        )
    else:
        await tg_bot.send_photo(chat_id=channel_id, photo=open(image_path, "rb"))
