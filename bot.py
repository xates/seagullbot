#!/usr/bin/env python3

import os
from http.server import HTTPServer, HTTPStatus, SimpleHTTPRequestHandler
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from telegram import *
from telegram.ext import *

APP_URL = os.getenv("APP_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT") or 8443)


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="www", **kwargs)

    def list_directory(self, path):
        self.send_error(HTTPStatus.NOT_FOUND, "File not found")


def make_meme(texts: list, offsets: list, template: str, target: str) -> None:
    img = Image.open(f"{template}.jpg")
    width = img.size[0]
    height = img.size[1]

    draw = ImageDraw.Draw(img)
    outline_size = 15

    for text, offset in zip(texts, offsets):
        # find biggest font size that fits
        font_size = 80
        font = ImageFont.truetype("impact.ttf", font_size)
        text_size = font.getsize(text)

        while text_size[0] > width - 20:
            font_size = font_size - 1
            font = ImageFont.truetype("impact.ttf", font_size)
            text_size = font.getsize(text)

        # compute position for text
        text_position_x = (width / 2) - (text_size[0] / 2)
        text_position_y = offset if offset >= 0 else height - text_size[1] - outline_size
        text_position = (text_position_x, text_position_y)

        # draw outlines
        # there might be a better way
        outline_range = int(font_size / outline_size)
        for x in range(-outline_range, outline_range + 1):
            for y in range(-outline_range, outline_range + 1):
                draw.text((text_position[0] + x, text_position[1] + y), text, (0, 0, 0), font=font)

        # draw text
        draw.text(text_position, text, (255, 255, 255), font=font)

    img.save(f"www/{target}.jpg")

    thumb_size = (200, 200)
    img.thumbnail(thumb_size)
    img.save(f"www/{target}-thumb.jpg")

    return width, height


def start(update: Update, context: CallbackContext) -> None:
    uuid = str(uuid4())
    make_meme(["THIS IS AN", "INLINE BOT!!1!!1"], [0, -1], "small", uuid)
    update.message.reply_photo(f"{APP_URL}{uuid}.jpg")


def inlinequery(update: Update, context: CallbackContext) -> None:
    texts = update.inline_query.query.upper().split("\n")

    n = len(texts)
    results = []

    if n == 1:
        uuid = str(uuid4())
        width, height = make_meme(texts, [-1], "small", uuid)
        results.append(
            InlineQueryResultPhoto(
                id=uuid,
                photo_url=f"{APP_URL}{uuid}.jpg",
                thumb_url=f"{APP_URL}{uuid}-thumb.jpg",
                photo_width=width,
                photo_height=height
            ))

    elif n == 2:
        uuid = str(uuid4())
        width, height = make_meme(texts, [0, -1], "small", uuid)
        results.append(
            InlineQueryResultPhoto(
                id=uuid,
                photo_url=f"{APP_URL}{uuid}.jpg",
                thumb_url=f"{APP_URL}{uuid}-thumb.jpg",
                photo_width=width,
                photo_height=height
            ))

        uuid = str(uuid4())
        texts.insert(1, "*INHALES*")
        width, height = make_meme(texts, [0, 665, -1], "medium", uuid)
        results.append(
            InlineQueryResultPhoto(
                id=uuid,
                photo_url=f"{APP_URL}{uuid}.jpg",
                thumb_url=f"{APP_URL}{uuid}-thumb.jpg",
                photo_width=width,
                photo_height=height
            ))

    elif n == 3:
        uuid = str(uuid4())
        width, height = make_meme(texts, [0, 665, -1], "medium", uuid)
        results.append(
            InlineQueryResultPhoto(
                id=uuid,
                photo_url=f"{APP_URL}{uuid}.jpg",
                thumb_url=f"{APP_URL}{uuid}-thumb.jpg",
                photo_width=width,
                photo_height=height
            ))

        uuid = str(uuid4())
        texts.insert(2, "*INHALES*")
        width, height = make_meme(texts, [0, 677, 1342, -1], "large", uuid)
        results.append(
            InlineQueryResultPhoto(
                id=uuid,
                photo_url=f"{APP_URL}{uuid}.jpg",
                thumb_url=f"{APP_URL}{uuid}-thumb.jpg",
                photo_width=width,
                photo_height=height
            ))

    elif n == 4:
        uuid = str(uuid4())
        width, height = make_meme(texts, [0, 677, 1342, -1], "large", uuid)
        results.append(
            InlineQueryResultPhoto(
                id=uuid,
                photo_url=f"{APP_URL}{uuid}.jpg",
                thumb_url=f"{APP_URL}{uuid}-thumb.jpg",
                photo_width=width,
                photo_height=height
            ))

    update.inline_query.answer(results)


def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(InlineQueryHandler(inlinequery))

    os.makedirs("www", exist_ok=True)
    httpd = HTTPServer(("", PORT), CustomHandler)

    updater.bot.delete_webhook()
    updater.start_polling()

    httpd.serve_forever()


if __name__ == "__main__":
    main()
