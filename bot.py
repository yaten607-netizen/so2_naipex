import logging
import os
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw"
# Бот сам возьмет ссылку на вечную базу из настроек Railway
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/postgres")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def init_db():
    """Создает вечную таблицу пользователей и рефералов"""
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            balance INT DEFAULT 0,
            referrals_count INT DEFAULT 0,
            referrer_id BIGINT
        )
    """)
    await conn.close()

async def add_user(user_id, username, referrer_id=None):
    """Добавляет юзера и железно засчитывает реферала пригласителю"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    exists = await conn.fetchrow("SELECT user_id FROM users WHERE user_id = $1", user_id)
    
    if not exists:
        if referrer_id and int(referrer_id) != user_id:
            ref_exists = await conn.fetchrow("SELECT user_id FROM users WHERE user_id = $1", int(referrer_id))
            if ref_exists:
                # Железно плюсуем реферала в базу данных
                await conn.execute("UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = $1", int(referrer_id))
                # Тут можно начислить бонусную голду за друга:
                # await conn.execute("UPDATE users SET balance = balance + 5 WHERE user_id = $1", int(referrer_id))
        else:
            referrer_id = None
            
        await conn.execute(
            "INSERT INTO users (user_id, username, referrer_id) VALUES ($1, $2, $3)",
            user_id, username, referrer_id
        )
    await conn.close()

async def get_user_data(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT balance, referrals_count FROM users WHERE user_id = $1", user_id)
    await conn.close()
    if row:
        return {"balance": row["balance"], "referrals_count": row["referrals_count"]}
    return {"balance": 0, "referrals_count": 0}

async def get_all_users():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    return [row["user_id"] for row in rows]

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
    
    await add_user(user_id, username, referrer_id)
    
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!\n\n"
        "Приглашай друзей, открывай кейсы и зарабатывай голду! 🔥"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu())

@dp.message(F.text == "👥 Рефералка")
async def referral_menu(message: types.Message):
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    user_data = await get_user_data(user_id)
    
    ref_text = (
        "👥 **Реферальная система StandHub**\n\n"
        f"🔗 **Твоя ссылка для приглашений:**\n`{ref_link}`\n\n"
        f"📊 У тебя приглашено друзей: **{user_data['referrals_count']}**\n\n"
        "Для вывода нужно пригласить минимум 5 друзей!"
    )
    await message.answer(ref_text, parse_mode="Markdown")

@dp.message(F.text == "💰 Вывод голды")
async def withdraw_gold(message: types.Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    
    user_balance = user_data['balance']
    user_referrals = user_data['referrals_count']
    
    if user_balance < 50 or user_referrals < 5:
        error_text = (
            "❌ **Отказ в выводе средств**\n\n"
            "Необходимые условия:\n"
            "1. Минимальный баланс: **50 голды**\n"
            "2. Минимальное количество рефералов: **5 друзей**\n\n"
            f"📊 Твои показатели:\n"
            f"• Баланс: {user_balance} голды\n"
            f"• Рефералы: {user_referrals} / 5 друзей"
        )
        await message.answer(error_text, parse_mode="Markdown")
    else:
        await message.answer("✅ Введите ваш ID в Standoff 2 для получения голды:")

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
        
    all_users = await get_all_users()
    success_count = 0
    for u_id in all_users:
        try:
            await bot.send_message(chat_id=u_id, text=broadcast_text)
            success_count += 1
        except Exception: pass
    await message.answer(f"📢 Рассылка завершена!\n✅ Отправлено: {success_count} пользователям.")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
