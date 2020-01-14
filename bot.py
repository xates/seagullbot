#!/usr/bin/env python3

import os
from http.server import HTTPServer, HTTPStatus, SimpleHTTPRequestHandler
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from telegram import *
from telegram.ext import *

APP_URL = os.getenv("APP_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT"))


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="www", **kwargs)

    def list_directory(self, path):
        self.send_error(HTTPStatus.NOT_FOUND, "File not found")


def make_meme(top_text: str, bottom_text: str, template: str, target: str) -> None:
    font_size = 72
    outline_size = 15

    img = Image.open(template)
    width = img.size[0]
    height = img.size[1]

    # find biggest font size that works
    font = ImageFont.truetype("impact.ttf", font_size)
    top_text_size = font.getsize(top_text)
    bottom_text_size = font.getsize(bottom_text)

    while top_text_size[0] > width - 20 or bottom_text_size[0] > width - 20:
        font_size = font_size - 1
        font = ImageFont.truetype("impact.ttf", font_size)
        top_text_size = font.getsize(top_text)
        bottom_text_size = font.getsize(bottom_text)

    # find top centered position for top text
    top_text_position_x = (width/2) - (top_text_size[0]/2)
    top_text_position_y = 0
    top_text_position = (top_text_position_x, top_text_position_y)

    # find bottom centered position for bottom text
    bottom_text_position_X = (width/2) - (bottom_text_size[0]/2)
    bottom_text_position_Y = height - bottom_text_size[1] - outline_size
    bottom_text_position = (bottom_text_position_X, bottom_text_position_Y)

    draw = ImageDraw.Draw(img)

    # draw outlines
    # there may be a better way
    outline_range = int(font_size / outline_size)
    for x in range(-outline_range, outline_range + 1):
        for y in range(-outline_range, outline_range + 1):
            draw.text((top_text_position[0] + x, top_text_position[1] + y), top_text, (0, 0, 0), font=font)
            draw.text((bottom_text_position[0] + x, bottom_text_position[1] + y), bottom_text, (0, 0, 0), font=font)

    draw.text(top_text_position, top_text, (255, 255, 255), font=font)
    draw.text(bottom_text_position, bottom_text, (255, 255, 255), font=font)

    img.save(f"www/i/{target}.jpg")

    thumb_size = (200, 200)
    img.thumbnail(thumb_size)
    img.save(f"www/i/{target}-thumb.jpg")

    return width, height


def start(update: Update, context: CallbackContext) -> None:
    uuid = str(uuid4())
    make_meme("THIS IS AN", "INLINE BOT!!1!!1", "seagull.jpg", uuid)
    update.message.reply_photo(f"{APP_URL}i/{uuid}.jpg")


def inlinequery(update: Update, context: CallbackContext) -> None:
    top_text, _, bottom_text = update.inline_query.query.upper().partition("\n")
    uuid = str(uuid4())
    width, height = make_meme(top_text if bottom_text else "",
                              bottom_text.replace("\n", " ") or top_text,
                              "seagull.jpg", uuid)

    results = [
        InlineQueryResultPhoto(
            id=uuid,
            photo_url=f"{APP_URL}i/{uuid}.jpg",
            thumb_url=f"{APP_URL}i/{uuid}-thumb.jpg",
            photo_width=width,
            photo_height=height
        )]

    update.inline_query.answer(results)


def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(InlineQueryHandler(inlinequery))

    os.makedirs("www/i", exist_ok=True)
    httpd = HTTPServer(("", PORT), CustomHandler)

    updater.bot.delete_webhook()
    updater.start_polling()

    httpd.serve_forever()


if __name__ == "__main__":
    main()
