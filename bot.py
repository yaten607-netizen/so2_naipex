import logging
import sqlite3
import random
import string
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)

# ================= ТВОИ НАСТРОЙКИ ВШИТЫ НАМЕРТВО =================
BOT_TOKEN = "8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw"
ADMIN_ID = 5376742900          # Твой личный Telegram ID
CHANNEL_ID = -1003940562373    # ID твоего канала для проверки подписки
CHANNEL_URL = "https://t.me/standhub_channel" # Ссылка для кнопки подписки
SUPPORT_USERNAME = "@fr7gment" # Твой саппорт юз
# =================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# База данных в папке /tmp, чтобы не затиралась при перезапусках кода
DB_NAME = os.path.join("/tmp", "database.db")

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            reward INTEGER,
            max_activations INTEGER,
            current_activations INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_promos (
            user_id INTEGER,
            code TEXT,
            PRIMARY KEY (user_id, code)
        )
    """)
    conn.commit()
    conn.close()

# --- Функции Базы Данных ---
def add_user(user_id, username, referrer_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    if not exists:
        if referrer_id and int(referrer_id) != user_id:
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (int(referrer_id),))
            if cursor.fetchone():
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
    return {"balance": result[0], "referrals_count": result[1]} if result else {"balance": 0, "referrals_count": 0}

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

init_db()

# --- Проверка подписки ---
async def check_subscription(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator", "restricted"]:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки подписки для {user_id}: {e}")
        return False

# --- Меню (Кейсы теперь в самом верху) ---
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    
    # 🎰 Кнопка кейсов на всю ширину первой строки
    builder.button(text="🎰 Открыть Кейсы", web_app=types.WebAppInfo(url="https://google.com"))
    
    # Остальные кнопки ниже
    builder.button(text="💰 Баланс")
    builder.button(text="💰 Вывод голды")
    builder.button(text="🎁 Промокод")
    builder.button(text="👥 Рефералка")
    builder.button(text="❓ Помощь")
    
    # Сетка кнопок: 1 на первой строке (кейсы), остальные по 2 в ряд
    builder.adjust(1, 2, 2, 1) 
    return builder.as_markup(resize_keyboard=True)

def get_sub_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Подписаться на канал", url=CHANNEL_URL)
    builder.button(text="✅ Проверить подписку", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()

# --- Команда /start ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    start_args = message.text.split()
    referrer_id = start_args[1] if len(start_args) > 1 else None
    
    add_user(user_id, username, referrer_id)
    
    if await check_subscription(user_id):
        welcome_text = (
            f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!\n\n"
            "Здесь ты можешь зарабатывать голду Standoff 2, приглашая друзей и активируя промокоды. 🔥"
        )
        await message.answer(welcome_text, reply_markup=get_main_menu())
    else:
        await message.answer(
            "🛑 **Доступ ограничен!**\n\nДля использования бота и открытия кейсов ты должен быть подписан на наш официальный канал!",
            reply_markup=get_sub_keyboard()
        )

@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.answer("🎉 Отлично, подписка подтверждена! Добро пожаловать!", reply_markup=get_main_menu())
        await call.message.delete()
    else:
        await call.answer("❌ Ты всё ещё не подписался на канал!", show_alert=True)

# --- Кнопка "💰 Баланс" ---
@dp.message(F.text == "💰 Баланс")
async def show_balance(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    balance_text = (
        "💳 **Твой игровой профиль:**\n\n"
        f"💰 Баланс: **{user_data['balance']} голды**\n"
        f"👥 Приглашено друзей: **{user_data['referrals_count']}**\n\n"
        "Зарабатывай голду в кейсах или приглашая друзей по реферальной ссылке! 🚀"
    )
    await message.answer(balance_text, parse_mode="Markdown")

# --- СКРЫТАЯ АДМИНКА ПО КОМАНДЕ /admin ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    all_users = get_all_users()
    total_users = len(all_users)
    
    await message.answer("📊 *Сбор статистики рассылки... Подожди секунду*")
    
    blocked_users = 0
    for u_id in all_users:
        try:
            await bot.send_chat_action(chat_id=u_id, action="typing")
        except Exception:
            blocked_users += 1
            
    active_users = total_users - blocked_users
    
    admin_text = (
        "👑 **Панель Администратора StandHub**\n\n"
        f"📊 **Статистика бота:**\n"
        f"• Всего пользователей в базе: `{total_users}`\n"
        f"• Активные (живые): `{active_users}`\n"
        f"• Заблокировали бота (мертвые): `{blocked_users}`\n\n"
        "⚙️ **Доступные команды:**\n"
        "👉 `/send_all Текст` — запустить рассылку\n"
        "👉 `/create_promo сумма активации` — создать промокод (Пример: `/create_promo 15 50` создаст промокод на 15 голды для 50 человек)"
    )
    await message.answer(admin_text, parse_mode="Markdown")

# --- Создание промокода (Только для админа) ---
@dp.message(lambda message: message.text and message.text.startswith('/create_promo'))
async def cmd_create_promo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Ошибка! Формат команды: `/create_promo [сколько_голды] [кол_во_активаций]`\nПример: `/create_promo 20 100`")
        return
        
    try:
        reward = int(args[1])
        max_acts = int(args[2])
    except ValueError:
        await message.answer("❌ Сумма и активации должны быть числами!")
        return
        
    code = "SH-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO promo_codes (code, reward, max_activations) VALUES (?, ?, ?)", (code, reward, max_acts))
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ **Промокод успешно создан!**\n\n🎫 Код: `{code}`\n💰 Награда: **{reward} голды**\n👥 Макс. активаций: **{max_acts}**")

# --- Кнопка "🎁 Промокод" (Ввод юзером) ---
@dp.message(F.text == "🎁 Промокод")
async def promo_code_menu(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    await message.answer("🎟 **Активация промокода**\n\nОтправь мне промокод прямо в этот чат:")

@dp.message(lambda message: message.text and message.text.startswith('SH-'))
async def activate_promo(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    user_id = message.from_user.id
    code = message.text.strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT reward, max_activations, current_activations FROM promo_codes WHERE code = ?", (code,))
    promo = cursor.fetchone()
    
    if not promo:
        await message.answer("❌ Такого промокода не существует или он введен неверно!")
        conn.close()
        return
        
    reward, max_acts, curr_acts = promo
    
    cursor.execute("SELECT user_id FROM user_promos WHERE user_id = ? AND code = ?", (user_id, code))
    already_used = cursor.fetchone()
    
    if already_used:
        await message.answer("❌ Ты уже активировал этот промокод!")
    elif curr_acts >= max_acts:
        await message.answer("😢 К сожалению, этот промокод уже закончился!")
    else:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, user_id))
        cursor.execute("UPDATE promo_codes SET current_activations = current_activations + 1 WHERE code = ?", (code,))
        cursor.execute("INSERT INTO user_promos (user_id, code) VALUES (?, ?)", (user_id, code))
        conn.commit()
        await message.answer(f"🎉 **Успех!** Промокод `{code}` активирован! Тебе начислено **{reward} голды**! 🔥")
        
    conn.close()

# --- Кнопки меню ---
@dp.message(F.text == "👥 Рефералка")
async def referral_menu(message: types.Message):
    if not await check_subscription(message.from_user.id): return
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
    if not await check_subscription(message.from_user.id): return
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
        await message.answer("✅ Введите ваш ID в Standoff 2 для получения голды:")

@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    help_text = f"🛠 **Поддержка StandHub**\n\nЕсли у вас возникли вопросы, проблемы с выводом или вы нашли баг, пишите нашему админу: {SUPPORT_USERNAME}"
    await message.answer(help_text)

# --- Рассылка по всей базе ---
@dp.message(lambda message: message.text and message.text.startswith('/send_all'))
async def admin_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    broadcast_text = message.text.replace('/send_all', '').strip()
    if not broadcast_text: return
        
    all_users = get_all_users()
    success_count = 0
    for u_id in all_users:
        try:
            await bot.send_message(chat_id=u_id, text=broadcast_text)
            success_count += 1
        except Exception: pass
    await message.answer(f"📢 Рассылка завершена!\n✅ Отправлено: {success_count} пользователям.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
