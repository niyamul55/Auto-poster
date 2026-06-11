import asyncio
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import os

# === CONFIG - Koyeb Env এ দিবা ===
BOT_TOKEN = os.getenv("BOT_TOKEN") # 8071595810:AAGqo4VDZCtv-lFr-ooduWOO-eSHYUOU2HA
ADMIN_ID = int(os.getenv("ADMIN_ID")) # 8071595810
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) # -1003542673004

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === DATABASE ===
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS channels
                 (id INTEGER PRIMARY KEY, channel_id TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  caption TEXT,
                  post_time TEXT,
                  posted INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('gap_minutes', '60')")
    conn.commit()
    conn.close()

# === /start ===
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "🤖 *Pro Mods BD Bot Active* 🔥\n\n"
        "📌 *Commands:*\n"
        "/add_channel - Channel Add করো\n"
        "/post - Post Schedule করো\n"
        "/setgap - কতক্ষণ পর পর Post হবে\n"
        "/list - Pending Post দেখো\n"
        "/help - সব Command\n\n"
        "✅ *Bot 24/7 Active Koyeb এ*",
        parse_mode="Markdown"
    )

# === /add_channel ===
class AddChannel(StatesGroup):
    get_link = State()

@dp.message(F.text == "/add_channel")
async def add_channel_start(message: Message, state: FSMContext):
    if message.from_user.id!= ADMIN_ID: return
    await state.set_state(AddChannel.get_link)
    await message.answer("📢 *Channel Username বা Link দাও:*\n\nযেমন: `@promodsbd` বা `https://t.me/promodsbd`", parse_mode="Markdown")

@dp.message(AddChannel.get_link)
async def add_channel_save(message: Message, state: FSMContext):
    try:
        channel = message.text.replace("https://t.me/", "@").strip()
        if not channel.startswith("@"): channel = "@" + channel

        chat = await bot.get_chat(channel)
        channel_id = chat.id

        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO channels (id, channel_id) VALUES (1,?)", (str(channel_id),))
        conn.commit()
        conn.close()

        await message.answer(f"✅ *Channel Add Done!*\n\n📢 Name: `{chat.title}`\n🆔 ID: `{channel_id}`\n\nএখন এই Channel এ Post যাবে", parse_mode="Markdown")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ *Error:* Bot কে Channel এ Admin বানাও নাই\n\n`{e}`", parse_mode="Markdown")

# === /setgap - কতখন পর পর পোস্ট করবে ===
class SetGap(StatesGroup):
    get_minutes = State()

@dp.message(F.text == "/setgap")
async def set_gap_start(message: Message, state: FSMContext):
    if message.from_user.id!= ADMIN_ID: return
    await state.set_state(SetGap.get_minutes)
    await message.answer("⏰ *কত মিনিট পর পর Post হবে?*\n\nসংখ্যা লিখো। যেমন: `72` = 1 ঘন্টা 12 মিনিট\n`60` = 1 ঘন্টা", parse_mode="Markdown")

@dp.message(SetGap.get_minutes)
async def set_gap_save(message: Message, state: FSMContext):
    try:
        minutes = int(message.text)
        if minutes < 1: raise ValueError

        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("UPDATE settings SET value=? WHERE key='gap_minutes'", (str(minutes),))
        conn.commit()
        conn.close()

        hours = minutes // 60
        mins = minutes % 60
        await message.answer(f"✅ *Gap Set Done!*\n\n⏱️ এখন থেকে `{hours} ঘন্টা {mins} মিনিট` পর পর Post হবে", parse_mode="Markdown")
        await state.clear()
    except:
        await message.answer("❌ শুধু সংখ্যা দাও। যেমন: `60`")

# === /post - Bulk Post Schedule ===
class BulkPost(StatesGroup):
    get_data = State()

@dp.message(F.text == "/post")
async def post_start(message: Message, state: FSMContext):
    if message.from_user.id!= ADMIN_ID: return
    await state.set_state(BulkPost.get_data)
    await message.answer(
        "📝 *Bulk Post Setup*\n\n"
        "Format:\n"
        "`Caption: তোমার পোস্টের লেখা`\n"
        "`Count: 20`\n"
        "`Start: 2026-06-12 18:00`\n\n"
        "📌 *Count:* কয়টা Post\n"
        "📌 *Start:* প্রথম Post কখন\n"
        "📌 Gap `/setgap` দিয়ে Set করা আছে",
        parse_mode="Markdown"
    )

@dp.message(BulkPost.get_data)
async def post_process(message: Message, state: FSMContext):
    try:
        lines = message.text.split('\n')
        caption = ""
        count = 0
        start_time = None

        for line in lines:
            if line.startswith("Caption:"):
                caption = line.replace("Caption:", "").strip()
            elif line.startswith("Count:"):
                count = int(line.replace("Count:", "").strip())
            elif line.startswith("Start:"):
                start_time = datetime.strptime(line.replace("Start:", "").strip(), "%Y-%m-%d %H:%M")

        if not all([caption, count, start_time]):
            await message.answer("❌ Data Missing")
            return

        # Gap Minutes বের করো DB থেকে
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='gap_minutes'")
        gap_minutes = int(c.fetchone()[0])
        conn.close()

        # Schedule করো
        for i in range(count):
            post_time = start_time + timedelta(minutes=i * gap_minutes)
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute("INSERT INTO posts (caption, post_time) VALUES (?,?)",
                      (caption, post_time.strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            conn.close()

        end_time = start_time + timedelta(minutes=(count-1) * gap_minutes)
        await message.answer(
            f"✅ *{count}টা Post Schedule Done!* 🔥\n\n"
            f"⏰ Start: `{start_time.strftime('%d %b, %I:%M %p')}`\n"
            f"⏰ End: `{end_time.strftime('%d %b, %I:%M %p')}`\n"
            f"⏱️ Gap: `{gap_minutes} Minutes`",
            parse_mode="Markdown"
        )
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Error: {e}")

# === /list ===
@dp.message(F.text == "/list")
async def cmd_list(message: Message):
    if message.from_user.id!= ADMIN_ID: return
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM posts WHERE posted=0")
    pending = c.fetchone()[0]
    c.execute("SELECT post_time, caption FROM posts WHERE posted=0 ORDER BY post_time LIMIT 5")
    next_posts = c.fetchall()
    conn.close()

    if pending == 0:
        await message.answer("📭 *No Pending Posts*", parse_mode="Markdown")
        return

    text = f"📊 *Pending Posts:* `{pending}`\n\n*Next 5:*\n"
    for p_time, cap in next_posts:
        text += f"• `{p_time}` - {cap[:30]}...\n"
    await message.answer(text, parse_mode="Markdown")

# === /help ===
@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "📚 *All Commands:*\n\n"
        "/start - Bot চালু\n"
        "/add_channel - Channel Add করো\n"
        "/setgap - Post এর Gap Set করো\n"
        "/post - Bulk Post Schedule\n"
        "/list - Pending Post দেখো\n"
        "/help - এই Help\n\n"
        "🤖 *Bot Public Group এ Post করবে*",
        parse_mode="Markdown"
    )

# === AUTO POST SCHEDULER ===
async def check_scheduled_posts():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE post_time=? AND posted=0", (now,))
        posts = c.fetchall()

        # Channel ID বের করো
        c.execute("SELECT channel_id FROM channels WHERE id=1")
        result = c.fetchone()
        target_channel = int(result[0]) if result else CHANNEL_ID

        for post in posts:
            post_id, caption, post_time, posted = post
            try:
                await bot.send_message(target_channel, caption, parse_mode="Markdown")
                c.execute("UPDATE posts SET posted=1 WHERE id=?", (post_id,))
                conn.commit()
                print(f"Posted: {post_id} at {now}")
            except Exception as e:
                print(f"Error posting {post_id}: {e}")
        conn.close()
        await asyncio.sleep(30)

# === START ===
async def main():
    init_db()
    asyncio.create_task(check_scheduled_posts())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
