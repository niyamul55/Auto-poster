import asyncio
import logging
import sqlite3
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# === CONFIG === Render Environment থেকে আসবে ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Moders_Niamul")
PANEL_PASSWORD = os.getenv("PANEL_PASSWORD", "niamulpro")
INVITE_LINK = os.getenv("INVITE_LINK", "https://t.me/+95v75sNs-RQ3ZTBl")
PORT = int(os.getenv("PORT", 10000))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN Environment Variable সেট করো নাই!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# === DATABASE ===
def init_db():
    conn = sqlite3.connect('promods.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER UNIQUE,
                  name TEXT,
                  username TEXT,
                  join_date TEXT)''')
    conn.commit()
    conn.close()

def add_user(user_id, name, username):
    conn = sqlite3.connect('promods.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (user_id, name, username, join_date) VALUES (?,?,?,?)",
                  (user_id, name, username or "NoUsername", datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_total_users():
    conn = sqlite3.connect('promods.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    conn.close()
    return total

def get_recent_users(limit=10):
    conn = sqlite3.connect('promods.db')
    c = conn.cursor()
    c.execute("SELECT name, username, join_date FROM users ORDER BY id DESC LIMIT?", (limit,))
    users = c.fetchall()
    conn.close()
    return users

# === AUTO APPROVE ===
@dp.chat_join_request()
async def approve_request(update: types.ChatJoinRequest):
    await update.approve()
    user = update.from_user
    add_user(user.id, user.full_name, user.username)
    total = get_total_users()
    try:
        await bot.send_message(
            user.id,
            f"✅ Welcome to Pro Mods BD ভাই!\n\n"
            f"🎉 তুমি {total} নাম্বার Member\n"
            f"🔥 Daily Pro APK Free\n"
            f"📌 Pin Post Check করো\n"
            f"👇 Problem: @{ADMIN_USERNAME}"
        )
    except:
        pass

# === ADMIN PANEL ===
async def admin_panel(request):
    if request.rel_url.query.get('pass')!= PANEL_PASSWORD:
        return web.Response(text="❌ Wrong Password", status=403)

    total = get_total_users()
    recent = get_recent_users(10)
    recent_html = "<br>".join([f"{i+1}. {u[0]} | @{u[1]} | {u[2]}" for i,u in enumerate(recent)]) if recent else "এখনো কেউ Join করে নাই"

    html = f"""
    <html><head><title>Pro Mods BD Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family:Arial; padding:15px; background:#0e1621; color:#fff; }}
      .card {{ background:#1e2936; padding:15px; border-radius:12px; margin:10px 0; }}
      .stat {{ font-size:32px; color:#2ea6ff; font-weight:bold; }}
        input,textarea {{ width:100%; padding:10px; margin:5px 0; background:#0e1621; color:#fff; border:1px solid #2ea6ff; border-radius:8px; box-sizing:border-box; }}
        button {{ width:100%; padding:12px; background:#2ea6ff; color:white; border:none; border-radius:8px; font-size:16px; margin:5px 0; cursor:pointer; }}
    </style>
    </head>
    <body>
        <h1>🔥 Pro Mods BD Panel</h1>
        <div class="card">
            <h3>📊 Live Stats</h3>
            <div class="stat">{total}</div>
            <p>Total Members Approved</p>
            <p>Channel: <code>{CHANNEL_ID}</code></p>
        </div>
        <div class="card">
            <h3>👥 Last 10 Members</h3>
            <div style="max-height:200px; overflow:auto; font-size:14px;">{recent_html}</div>
        </div>
        <div class="card">
            <h3>📱 New Post with Button</h3>
            <form action="/post" method="post">
                <input type="hidden" name="pass" value="{PANEL_PASSWORD}">
                <textarea name="caption" rows="6">🎬 Video Editor Pro 18.1.0&#10;&#10;✅ Network Error Fix&#10;✅ No Watermark&#10;✅ All Premium Unlock&#10;&#10;⚡ Size: 233.7 MB&#10;&#10;👇 Pro Version লাগলে Button চাপো</textarea>
                <input type="text" name="btn_text" value="🔥 Request Pro APK">
                <input type="text" name="btn_url" value="https://t.me/{ADMIN_USERNAME}">
                <button type="submit">📤 Channel এ Post করো</button>
            </form>
        </div>
    </body></html>
    """
    return web.Response(text=html, content_type='text/html')

async def handle_post(request):
    data = await request.post()
    if data.get('pass')!= PANEL_PASSWORD:
        return web.Response(text="❌ Wrong Password", status=403)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=data.get('btn_text'), url=data.get('btn_url'))],
        [InlineKeyboardButton(text="👥 Share Friends", url=f"https://t.me/share/url?url={INVITE_LINK}")]
    ])
    await bot.send_message(CHANNEL_ID, data.get('caption'), reply_markup=keyboard)
    return web.Response(text=f"✅ Post Done! <a href='/admin?pass={PANEL_PASSWORD}'>Back</a>", content_type='text/html')

async def health_check(request):
    return web.Response(text="Bot is Running ✅")

async def main():
    init_db()
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/admin', admin_panel)
    app.router.add_post('/post', handle_post)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Panel: /admin?pass={PANEL_PASSWORD}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
