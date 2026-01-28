import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
from datetime import datetime, timedelta
import pytz

api_id = 23778342
api_hash = "9525e6f6e968605d773e16a33a4fcf62"

group_link = "https://t.me/+26cY61ypdHYwMDc1"
BOT_TOKEN = "8582125531:AAGrECSl468yNqeGvfnPA1c4RVkgv5BypjQ"
CHAT_ID = 811294158

IST = pytz.timezone("Asia/Kolkata")

client = TelegramClient("admin_alert", api_id, api_hash).start(bot_token=BOT_TOKEN)

admin_stats = {}
join_cache = set()

async def get_admins():
    group = await client.get_entity(group_link)
    admins = await client.get_participants(group, filter=ChannelParticipantsAdmins)
    return {a.id: (a.first_name or "Unknown") for a in admins}

async def send(msg):
    await client.send_message(CHAT_ID, msg)

@client.on(events.NewMessage(pattern='/status'))
async def status(event):
    await event.reply("✅ Bot Running\n⚡ PRO Admin Tracker Active")

@client.on(events.NewMessage(pattern='/today'))
async def today(event):
    txt = "📊 Today's Admin Activity:\n\n"
    for k,v in admin_stats.items():
        txt += f"{v['name']} : {v['count']} msgs\n"
    await event.reply(txt or "No data")

@client.on(events.NewMessage(pattern='/topadmins'))
async def topadmins(event):
    ranking = sorted(admin_stats.values(), key=lambda x: x['count'], reverse=True)
    txt = "🏆 Top Active Admins:\n\n"
    for i,a in enumerate(ranking[:10],1):
        txt += f"{i}. {a['name']} - {a['count']}\n"
    await event.reply(txt or "No data")

@client.on(events.ChatAction)
async def join_leave(event):
    if event.user_joined or event.user_added:
        await send(f"👤 Admin Joined: {event.user.first_name}")
    if event.user_left or event.user_kicked:
        await send(f"👋 Admin Left: {event.user.first_name}")

async def monitor():
    admins = await get_admins()
    await send("🤖 PRO ADMIN TRACKER STARTED\nMonitoring active...")

    while True:
        async for msg in client.iter_messages(group_link, limit=30):
            if msg.sender_id in admins:
                aid = msg.sender_id
                if aid not in admin_stats:
                    admin_stats[aid] = {
                        "name": admins[aid],
                        "count": 0
                    }
                admin_stats[aid]["count"] += 1
        await asyncio.sleep(300)

client.loop.create_task(monitor())
client.run_until_disconnected()
