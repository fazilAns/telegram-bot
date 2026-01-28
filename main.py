import os
from datetime import datetime, timedelta
from telethon import TelegramClient, events

# ========== Railway Environment Variables ==========
try:
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = int(os.getenv("CHAT_ID", "0"))
except Exception as e:
    raise ValueError(f"❌ ENV ERROR: {e}")

if not all([API_ID, API_HASH, BOT_TOKEN, CHAT_ID]):
    raise ValueError("❌ One or more environment variables missing!")

# ========== ADMIN IDS ==========
ADMIN_IDS = [
    123456789,
    987654321,
    1122334455,
]

# ========== Telegram Client ==========
client = TelegramClient("railway_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

admin_online = {}

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

@client.on(events.ChatAction)
async def admin_join_leave(event):
    if not (event.user_joined or event.user_left):
        return

    try:
        user = await event.get_user()
        if not user or user.id not in ADMIN_IDS:
            return

        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        now = datetime.now()

        if event.user_joined:
            admin_online[user.id] = now
            await client.send_message(
                CHAT_ID,
                f"🟢 ADMIN ONLINE\n\n"
                f"👤 {name}\n"
                f"🕒 {now.strftime('%I:%M %p')}"
            )

        elif event.user_left:
            start = admin_online.pop(user.id, None)
            if start:
                duration = (now - start).total_seconds()
                await client.send_message(
                    CHAT_ID,
                    f"🔴 ADMIN OFFLINE\n\n"
                    f"👤 {name}\n"
                    f"🟢 Online : {start.strftime('%I:%M %p')}\n"
                    f"🔴 Offline : {now.strftime('%I:%M %p')}\n"
                    f"⏱ Duration : {format_time(duration)}"
                )

    except Exception as e:
        print("❌ Tracker Error:", e)

print("🔥 Admin Online / Offline Tracker Started Successfully")
client.run_until_disconnected()
# redeploy fix

