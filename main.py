import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
import pytz
from collections import defaultdict

# ================== YOUR CONFIG ==================

api_id = 23778342
api_hash = "9525e6f6e968605d773e16a33a4fcf62"

group_link = "https://t.me/+26cY61ypdHYwMDc1"

BOT_TOKEN = "8582125531:AAGrECSl468yNqeGvfnPA1c4RVkgv5BypjQ"
CHAT_ID = "811294158"

# ================================================

IST = pytz.timezone("Asia/Kolkata")

client = TelegramClient("admin_alert", api_id, api_hash)
bot = Bot(token=BOT_TOKEN)

last_alert_time = None
activity_log = defaultdict(list)

# ================= BOT COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *PRO ADMIN TRACKER BOT*\n\n"
        "Commands:\n"
        "/status – Bot status\n"
        "/today – Today admin activity\n"
        "/week – Weekly activity\n"
        "/topadmins – Top active admins\n",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot Running\n"
        f"⏰ {datetime.now(IST).strftime('%I:%M %p IST')}"
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_date = datetime.now(IST).date()
    data = []

    for admin, times in activity_log.items():
        count = sum(1 for t in times if t.date() == today_date)
        if count:
            data.append(f"{admin}: {count}")

    if not data:
        await update.message.reply_text("❌ No admin activity today")
    else:
        await update.message.reply_text("📊 *Today Activity*\n\n" + "\n".join(data), parse_mode="Markdown")

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(IST)
    data = []

    for admin, times in activity_log.items():
        count = sum(1 for t in times if (now - t).days <= 7)
        if count:
            data.append(f"{admin}: {count}")

    if not data:
        await update.message.reply_text("❌ No admin activity this week")
    else:
        await update.message.reply_text("📈 *Weekly Activity*\n\n" + "\n".join(data), parse_mode="Markdown")

async def topadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ranking = sorted(activity_log.items(), key=lambda x: len(x[1]), reverse=True)[:5]

    if not ranking:
        await update.message.reply_text("❌ No admin data yet")
        return

    msg = "🏆 *Top Active Admins*\n\n"
    for i, (admin, times) in enumerate(ranking, 1):
        msg += f"{i}. {admin} — {len(times)} msgs\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ================= ADMIN JOIN / LEAVE ALERT =================

@client.on(events.ChatAction)
async def handler(event):
    if event.chat and str(event.chat.id).endswith(group_link.split("/")[-1]):
        return

    if event.user_joined or event.user_added:
        user = await event.get_user()
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"➕ *User Joined*\n\n👤 {user.first_name}",
            parse_mode="Markdown"
        )

    if event.user_left or event.user_kicked:
        user = await event.get_user()
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"➖ *User Left*\n\n👤 {user.first_name}",
            parse_mode="Markdown"
        )

# ================= MAIN TRACKER =================

async def main_tracker():
    global last_alert_time

    await client.start()
    group = await client.get_entity(group_link)
    admins = await client.get_participants(group, filter=ChannelParticipantsAdmins)
    admin_map = {a.id: (a.first_name or "Unknown") for a in admins}

    await bot.send_message(chat_id=CHAT_ID, text="🤖 PRO ADMIN TRACKER STARTED\nMonitoring admins + join/leave...")

    print("✅ PRO ADMIN TRACKER RUNNING...")

    while True:
        count = 0
        active_names = set()
        times = []

        async for msg in client.iter_messages(group, limit=50):
            if msg.sender_id in admin_map:
                name = admin_map[msg.sender_id]
                t = msg.date.astimezone(IST)

                count += 1
                active_names.add(name)
                times.append(t)
                activity_log[name].append(t)

        if count >= 4:
            now = datetime.now(IST)

            if not last_alert_time or (now - last_alert_time).seconds > 1800:
                start_time = min(times)
                end_time = max(times)
                duration = int((end_time - start_time).total_seconds() / 60)

                text = (
                    f"🚨 *ADMINS ACTIVE*\n\n"
                    f"⏰ {now.strftime('%I:%M %p')} IST\n"
                    f"👥 {', '.join(active_names)}\n"
                    f"📊 Messages: {count}\n\n"
                    f"🕐 From: {start_time.strftime('%I:%M %p')}\n"
                    f"🕐 To: {end_time.strftime('%I:%M %p')}\n"
                    f"⏳ Duration: {duration} min"
                )

                await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
                last_alert_time = now

        await asyncio.sleep(300)

# ================= RUN BOTH =================

async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("topadmins", topadmins))

    asyncio.create_task(main_tracker())
    await app.run_polling()

asyncio.run(run())
