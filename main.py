import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from loguru import logger

from get_screen import get_screen
from send_notification import send_win_notification

GREEN_COLOR = (99, 212, 100)
RED_COLOR = (212, 99, 100)

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_ID = os.getenv('TELEGRAM_ID')

logger.add("logs/{time}.log")


def send_message(text: str, img) -> None:
    async def send_async_message(message, image):
        bot = Bot(token=TELEGRAM_TOKEN)
        try:
            photo = FSInputFile(image)
            await bot.send_photo(chat_id=TELEGRAM_ID, photo=photo, caption=message)
        finally:
            await bot.session.close()
    if TELEGRAM_TOKEN and TELEGRAM_ID:
        asyncio.run(send_async_message(text, img))
    logger.info(text)


def load_seeds():
    seeds_path = BASE_DIR / "seeds.json"
    with open(seeds_path, 'r', encoding='utf-8') as seeds_file:
        seeds = json.load(seeds_file)
    return seeds


@logger.catch
def main():
    images_path = BASE_DIR / 'images'
    images_path.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    img_path = images_path / f'{now}.jpg'
    img = get_screen('Fortnite', img_path)
    img = img.convert("RGB")

    restock_seeds = []
    to_get_seeds = []
    no_restock_seeds = []
    undefined_color = []
    for seed in load_seeds():
        pixel_color = img.getpixel((seed['x'], seed['y']))
        if pixel_color == GREEN_COLOR:
            restock_seeds.append(seed)
            if seed['notification']:
                to_get_seeds.append(seed)
        elif pixel_color == RED_COLOR:
            no_restock_seeds.append(seed)
        else:
            undefined_color.append((seed, pixel_color))

    if to_get_seeds:
        to_get_seeds.reverse()
        message = "\n".join([f"{i + 1}. {seed['name']}" for i, seed in enumerate(to_get_seeds)])
        message = f"Доступно к покупке:\n{message}"
        send_message(message, img_path)
        send_win_notification(message)

    if (restock_seeds or no_restock_seeds) and undefined_color:
        lines = [f"{i + 1}. x:{seed[0]['x']} y:{seed[0]['y']} - {seed[1]}" for i, seed in enumerate(undefined_color)]
        message = "\n".join(lines)
        message = f"Неизвестные цвета:\n{message}"
        send_message(message, img_path)
        send_win_notification("Проверь магазин + Неизвестные цвета")
    elif undefined_color:
        send_win_notification("Проверь магазин")


def get_next_time(now):
    times = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    times.reverse()
    minute = now.minute
    next_time = now + timedelta(minutes=5)
    if minute >= 55:
        next_time = datetime(next_time.year, next_time.month, next_time.day, next_time.hour, 0, 30)
    else:
        for t in times:
            if minute >= t:
                next_time = datetime(next_time.year, next_time.month, next_time.day, next_time.hour, t + 5, 30)
                break
    return next_time


def five():
    while True:
        now = datetime.now()
        next_time = get_next_time(now)
        main()
        sleep_time = next_time.timestamp() - time.time()
        logger.info(f"Спим до {next_time} ({sleep_time:.2f} с)")
        time.sleep(sleep_time)


if __name__ == '__main__':
    five()
