import logging
import sqlite3
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем базу прямо в папке бота
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            referrals_count INTEGER DEFAULT 0,
            referrer_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username, referrer_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    
    if not exists:
        if referrer_id and int(referrer_id) != user_id:
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (int(referrer_id),))
            ref_exists = cursor.fetchone()
            if ref_exists:
                cursor.execute("UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?", (int(referrer_id),))
        else:
            referrer_id = None
            
        cursor.execute("INSERT INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)", (user_id, username, referrer_id))
        conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, referrals_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"balance": result[0], "referrals_count": result[1]}
    return {"balance": 0, "referrals_count": 0}

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

init_db()

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💰 Вывод голды")
    builder.button(text="🎁 Промокод")
    builder.button(text="👥 Рефералка")
    builder.button(text="❓ Помощь")
    builder.button(text="🎰 Открыть Кейсы", web_app=types.WebAppInfo(url="https://google.com"))
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    start_args = message.text.split()
    referrer_id = start_args[1] if len(start_args) > 1 else None
    
    add_user(user_id, username, referrer_id)
    
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!\n\n"
        "Здесь ты можешь зарабатывать голду Standoff 2, приглашая друзей и активируя промокоды. 🔥"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu())

@dp.message(F.text == "👥 Рефералка")
async def referral_menu(message: types.Message):
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    user_data = get_user_data(user_id)
    
    ref_text = (
        "👥 **Реферальная система StandHub**\n\n"
        f"🔗 **Твоя ссылка для приглашений:**\n`{ref_link}`\n\n"
        f"📊 У тебя приглашено друзей: **{user_data['referrals_count']}**\n\n"
        "За каждого друга ты получаешь голду! Для вывода нужно пригласить минимум 5 друзей."
    )
    await message.answer(ref_text, parse_mode="Markdown")

@dp.message(F.text == "💰 Вывод голды")
async def withdraw_gold(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    user_balance = user_data['balance']
    user_referrals = user_data['referrals_count']
    
    if user_balance < 50 or user_referrals < 5:
        error_text = (
            "❌ **Отказ в выводе средств**\n\n"
            "Для вывода голды должны быть выполнены **оба условия**:\n"
            "1. Минимальный баланс: **50 голды**\n"
            "2. Минимальное количество рефералов: **5 друзей**\n\n"
            f"📊 Твои текущие показатели:\n"
            f"• Баланс: {user_balance} голды\n"
            f"• Рефералы: {user_referrals} / 5 друзей"
        )
        await message.answer(error_text, parse_mode="Markdown")
    else:
        await message.answer("✅ Введите количество голды для вывода и укажите ваш ID в Standoff 2:")

@dp.message(F.text == "🎁 Промокод")
async def promo_code(message: types.Message):
    await message.answer("🎟 **Активация промокода**\n\nВведите ваш промокод в ответ на это сообщение:")

@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    help_text = "🛠 **Поддержка StandHub**\n\nПо всем вопросам пишите создателю бота."
    await message.answer(help_text)

@dp.message(lambda message: message.text and message.text.startswith('/send_all'))
async def admin_broadcast(message: types.Message):
    broadcast_text = message.text.replace('/send_all', '').strip()
    if not broadcast_text: return
        
    all_users = get_all_users()
    success_count = 0
    for u_id in all_users:
        try:
            await bot.send_message(chat_id=u_id, text=broadcast_text)
            success_count += 1
        except Exception: pass
    await message.answer(f"📢 Рассылка завершена!\n✅ Успешно отправлено: {success_count} пользователям.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
