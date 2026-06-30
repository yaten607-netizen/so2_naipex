import asyncio
import logging
import sqlite3
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Твой токен уже здесь, всё чётко
BOT_TOKEN = "8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КОНФИГУРАЦИЯ ---
ORIGIN_CASE_PRICE = 50.0
WEB_APP_URL = "https://google.com" # Временная заглушка, пока не создадим сайт-рулетку

# --- БАЗА ДАННЫХ (SQLite) ---
def init_db():
    conn = sqlite3.connect("standoff_drop.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0.0,
        referred_by INTEGER DEFAULT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skin_name TEXT,
        skin_price REAL
    )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("standoff_drop.db")
    cur = conn.cursor()
    cur.execute("SELECT balance, referred_by FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def add_user(user_id, referrer_id=None):
    conn = sqlite3.connect("standoff_drop.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referrer_id))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def add_balance(user_id, amount):
    conn = sqlite3.connect("standoff_drop.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_inventory(user_id):
    conn = sqlite3.connect("standoff_drop.db")
    cur = conn.cursor()
    cur.execute("SELECT skin_name FROM inventory WHERE user_id = ?", (user_id,))
    skins = cur.fetchall()
    conn.close()
    return [s[0] for s in skins]

# --- НИЖНИЕ КНОПКИ (Главное меню) ---
def main_reply_menu():
    kb = [
        [KeyboardButton(text="🎰 Кейсы (Web App)", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="📱 Мой Профиль"), KeyboardButton(text="👥 Рефералка")],
        [KeyboardButton(text="📈 Магазин Голды")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- ХЕНДЛЕРЫ ---

@dp.message(F.text.startswith("/start"))
async def start_cmd(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id == user_id:
            referrer_id = None

    is_new = add_user(user_id, referrer_id)
    welcome = "👋 Добро пожаловать в **StandHub**!\n\n🔥 Используй кнопки внизу экрана, чтобы открывать кейсы в Web App, копить голду и прокачивать инвентарь!"
    
    if is_new and referrer_id:
        add_balance(user_id, 10.0)  # Даем 10 голды для теста
        add_balance(referrer_id, 5.0)  
        welcome += "\n\n🎁 Тебе начислено **10.00 Голды** за переход по ссылке друга!"
        try:
            await bot.send_message(chat_id=referrer_id, text=f"🔔 По твоей ссылке зарегистрировался игрок @{message.from_user.username}! Тебе начислено **5.00 Голды**.")
        except:
            pass

    await message.answer(welcome, reply_markup=main_reply_menu(), parse_mode="Markdown")

@dp.message(F.text == "📱 Мой Профиль")
async def show_profile(message: Message):
    user_data = get_user(message.from_user.id)
    balance = user_data[0] if user_data else 0.0
    
    skins = get_inventory(message.from_user.id)
    inv_text = "\n".join([f"▪️ {s}" for s in skins]) if skins else "Пусто"
    
    text = (
        "📱 **Твой Профиль в StandHub:**\n\n"
        f"🆔 Ваш ID: `{message.from_user.id}`\n"
        f"💰 Баланс: **{balance:.2f} Голды**\n\n"
        f"🎒 **Твой инвентарь:**\n{inv_text}\n\n"
        "Вывод голды доступен от 100 Голды."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "👥 Рефералка")
async def referral_menu(message: Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    
    conn = sqlite3.connect("standoff_drop.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (message.from_user.id,))
    ref_count = cur.fetchone()[0]
    conn.close()
    
    text = (
        "👥 **Реферальная система:**\n\n"
        "🎁 Награда за друга: **5.00 Голды**\n"
        "🎁 Награда другу: **2.00 Голды** при старте\n\n"
        f"👥 Ты уже пригласил: **{ref_count}** чел.\n\n"
        f"🔗 **Твоя ссылка для друзей:**\n`{ref_link}`"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "📈 Магазин Голды")
async def shop_gold_plug(message: Message):
    await message.answer("📈 Магазин прямой покупки голды откроется в следующем обновлении.")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())