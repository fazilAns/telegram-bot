import asyncio
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins
from telegram import Bot
from datetime import datetime
import pytz

api_id = 23778342
api_hash = "9525e6f6e968605d773e16a33a4fcf62"

group_link = "https://t.me/+26cY61ypdHYwMDc1"

BOT_TOKEN = "8582125531:AAGrECSl468yNqeGvfnPA1c4RVkgv5BypjQ"
CHAT_ID = "811294158"

IST = pytz.timezone("Asia/Kolkata")

client = TelegramClient("admin_alert", api_id, api_hash)
bot = Bot(token=BOT_TOKEN)

async def main():
    await client.start()
    group = await client.get_entity(group_link)
    admins = await client.get_participants(group, filter=ChannelParticipantsAdmins)

    admin_map = {a.id: (a.first_name or "Unknown") for a in admins}

    print("✅ Monitoring admin activity (IST)...")

    last_alert_time = None

    while True:
        count = 0
        active_names = set()

        async for msg in client.iter_messages(group, limit=30):
            if msg.sender_id in admin_map:
                count += 1
                active_names.add(admin_map[msg.sender_id])

        if count >= 4:
            now = datetime.now(IST)
            if not last_alert_time or (now - last_alert_time).seconds > 1800:
                text = (
                    f"🚨 ADMINS ACTIVE NOW\n\n"
                    f"⏰ Time: {now.strftime('%I:%M %p')} IST\n"
                    f"👥 Active: {', '.join(active_names)}\n"
                    f"📊 Messages: {count}"
                )

                await bot.send_message(chat_id=CHAT_ID, text=text)
                last_alert_time = now

        await asyncio.sleep(300)  # check every 5 minutes

with client:
    client.loop.run_until_complete(main())
