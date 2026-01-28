import asyncio
import hashlib
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins
from telegram import Bot
from datetime import datetime
import pytz

# 🔐 YOUR CONFIG (Already filled)
api_id = 23778342
api_hash = "9525e6f6e968605d773e16a33a4fcf62"

group_link = "https://t.me/+26cY61ypdHYwMDc1"

BOT_TOKEN = "8582125531:AAGrECSl468yNqeGvfnPA1c4RVkgv5BypjQ"
CHAT_ID = "811294158"

IST = pytz.timezone("Asia/Kolkata")

client = TelegramClient("admin_alert", api_id, api_hash)
bot = Bot(token=BOT_TOKEN)

last_alert_time = None
last_admin_hash = None
admin_activity = {}
daily_reset_done = False


async def main():
    global last_alert_time, last_admin_hash, daily_reset_done

    await client.start()
    group = await client.get_entity(group_link)

    # 🤖 BOT START MESSAGE
    start_msg = (
        f"🤖 BOT STARTED SUCCESSFULLY\n\n"
        f"⏰ Time: {datetime.now(IST).strftime('%I:%M %p')} IST\n"
        f"✅ Admin Monitoring Active"
    )
    await bot.send_message(chat_id=CHAT_ID, text=start_msg)

    print("✅ PRO ADMIN TRACKER RUNNING...")

    while True:

        admins = await client.get_participants(group, filter=ChannelParticipantsAdmins)
        admin_map = {a.id: (a.first_name or "Unknown") for a in admins}

        # 🔔 ADMIN JOIN / LEAVE DETECTION
        admin_ids = sorted(admin_map.keys())
        current_hash = hashlib.md5(str(admin_ids).encode()).hexdigest()

        if last_admin_hash and last_admin_hash != current_hash:
            alert = "⚠️ ADMIN CHANGE DETECTED\n\n👥 Current Admins:\n"
            alert += "\n".join(admin_map.values())
            await bot.send_message(chat_id=CHAT_ID, text=alert)

        last_admin_hash = current_hash

        count = 0
        active_names = set()
        times = []

        async for msg in client.iter_messages(group, limit=40):
            if msg.sender_id in admin_map:
                name = admin_map[msg.sender_id]
                count += 1
                active_names.add(name)
                times.append(msg.date.astimezone(IST))
                admin_activity[name] = admin_activity.get(name, 0) + 1

        # 🚨 ACTIVITY ALERT
        if count >= 4:
            now = datetime.now(IST)

            if not last_alert_time or (now - last_alert_time).seconds > 1800:
                start_time = min(times)
                end_time = max(times)
                duration = end_time - start_time
                minutes = int(duration.total_seconds() / 60)

                ranking = sorted(admin_activity.items(), key=lambda x: x[1], reverse=True)[:5]
                rank_text = "\n".join([f"{i+1}. {n} — {c} msgs" for i,(n,c) in enumerate(ranking)])

                text = (
                    f"🚨 ADMINS ACTIVE NOW\n\n"
                    f"⏰ Time: {now.strftime('%I:%M %p')} IST\n"
                    f"👥 Active: {', '.join(active_names)}\n"
                    f"📊 Messages: {count}\n\n"
                    f"🕐 From: {start_time.strftime('%I:%M %p')}\n"
                    f"🕐 To: {end_time.strftime('%I:%M %p')}\n"
                    f"⏳ Duration: {minutes} min\n\n"
                    f"🏆 ADMIN RANKING\n{rank_text}"
                )

                await bot.send_message(chat_id=CHAT_ID, text=text)
                last_alert_time = now

        # 📊 DAILY SUMMARY @12AM
        now = datetime.now(IST)
        if now.hour == 0 and now.minute < 5 and not daily_reset_done:
            if admin_activity:
                ranking = sorted(admin_activity.items(), key=lambda x: x[1], reverse=True)

                report = (
                    "📊 DAILY ADMIN REPORT\n\n"
                    f"🥇 Most Active: {ranking[0][0]} — {ranking[0][1]} msgs\n"
                    f"👥 Total Admin Msgs: {sum(admin_activity.values())}"
                )
                await bot.send_message(chat_id=CHAT_ID, text=report)

            admin_activity.clear()
            daily_reset_done = True

        if now.hour == 1:
            daily_reset_done = False

        await asyncio.sleep(300)


with client:
    client.loop.run_until_complete(main())
