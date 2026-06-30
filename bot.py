import logging
import sqlite3
import random
import string
import os
import json
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

# ССЫЛКА НА ТВОЙ БУДУЩИЙ САЙТ С КЕЙСАМИ (заменишь потом на свою ссылку GitHub Pages)
WEBAPP_URL = "https://google.com" 
# =================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_DIR = "/app/data"
DB_NAME = os.path.join(DB_DIR, "database.db")

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица юзеров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            referrals_count INTEGER DEFAULT 0,
            referrer_id INTEGER
        )
    """)
    
    # Таблица инвентаря (выбитые скины)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            item_price INTEGER
        )
    """)
    
    # Таблица промокодов
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
            user_id INTEGER, code TEXT, PRIMARY KEY (user_id, code)
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

# Добавление скина в инвентарь юзера
def add_to_inventory(user_id, item_name, item_price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (user_id, item_name, item_price) VALUES (?, ?, ?)", (user_id, item_name, item_price))
    conn.commit()
    conn.close()

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

# --- Главное Меню ---
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="💰 Баланс")
    builder.button(text="💰 Вывод голды")
    builder.button(text="🎁 Промокод")
    builder.button(text="👥 Рефералка")
    builder.button(text="❓ Помощь")
    
    # Кнопка кейсов теперь ведет на наш будущий сайт WEBAPP_URL
    builder.button(text="🎰 Открыть Кейсы", web_app=types.WebAppInfo(url=WEBAPP_URL))
    
    builder.adjust(2, 2, 1, 1) 
    return builder.as_markup(resize_keyboard=True)

def get_sub_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Подписаться на канал", url=CHANNEL_URL)
    builder.button(text="✅ Проверить подписку", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()

# --- Обработка команды /start ---
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
            "Здесь ты можешь зарабатывать голду Standoff 2, открывать кейсы и активировать промокоды. 🔥"
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

# --- ЛОВИМ ДАННЫЕ ИЗ ВЕБ-САЙТА (ОТКРЫТИЕ КЕЙСА) ---
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    user_id = message.from_user.id
    
    try:
        # Сайт вернет json с инфой о кейсе и дропе
        data = json.loads(message.web_app_data.data)
        case_cost = int(data.get("case_cost", 0))    # Цена кейса
        dropped_item = data.get("item_name", "Скин") # Название скина
        item_price = int(data.get("item_price", 0))  # Стоимость скина в голде
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Проверяем, хватает ли у юзера голды на открытие кейса
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        balance = cursor.fetchone()[0]
        
        if balance < case_cost:
            await message.answer("❌ **Ошибка!** У вас недостаточно голды на балансе для открытия этого кейса!")
            conn.close()
            return
            
        # Списываем стоимость кейса и сразу зачисляем голду за скин (авто-продажа скина боту)
        # Если хочешь, чтобы скин падал в инвентарь, а не продавался сразу, уберем `+ item_price`
        new_balance = balance - case_cost + item_price
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        conn.close()
        
        # Добавляем действие в инвентарь на всякий случай
        add_to_inventory(user_id, dropped_item, item_price)
        
        result_text = (
            f"🎰 **Кейс успешно открыт!**\n\n"
            f"📉 Списано за кейс: -{case_cost} голды\n"
            f"🎉 Вы задропали: **{dropped_item}**\n"
            f"💰 Авто-продажа скина: +{item_price} голды!\n\n"
            f"💳 Текущий баланс: **{new_balance} голды**"
        )
        await message.answer(result_text, parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Ошибка WebApp данных: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке открытия кейса.")

# --- Остальные команды (Админка, Промокоды, Рефералка) ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    all_users = get_all_users()
    await message.answer(f"👑 **Панель Администратора**\n\nВсего пользователей: `{len(all_users)}`\n\n`/create_promo [голда] [активации]`\n`/send_all [текст]`")

@dp.message(lambda message: message.text and message.text.startswith('/create_promo'))
async def cmd_create_promo(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 3: return
    reward, max_acts = int(args[1]), int(args[2])
    code = "SH-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO promo_codes (code, reward, max_activations) VALUES (?, ?, ?)", (code, reward, max_acts))
    conn.commit()
    conn.close()
    await message.answer(f"✅ Промокод создан: `{code}` на {reward} голды ({max_acts} акт.)")

@dp.message(F.text == "🎁 Промокод")
async def promo_code_menu(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    await message.answer("🎟 Отправь мне промокод прямо в этот чат:")

@dp.message(lambda message: message.text and message.text.startswith('SH-'))
async def activate_promo(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id): 
        await message.answer("🛑 Вы должны быть подписаны на канал!")
        return
    code = message.text.strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT reward, max_activations, current_activations FROM promo_codes WHERE code = ?", (code,))
    promo = cursor.fetchone()
    if not promo:
        await message.answer("❌ Промокод не найден!")
        conn.close()
        return
    reward, max_acts, curr_acts = promo
    cursor.execute("SELECT user_id FROM user_promos WHERE user_id = ? AND code = ?", (user_id, code))
    if cursor.fetchone():
        await message.answer("❌ Уже активирован!")
    elif curr_acts >= max_acts:
        await message.answer("😢 Закончился!")
    else:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, user_id))
        cursor.execute("UPDATE promo_codes SET current_activations = current_activations + 1 WHERE code = ?", (code,))
        cursor.execute("INSERT INTO user_promos (user_id, code) VALUES (?, ?)", (user_id, code))
        conn.commit()
        await message.answer(f"🎉 Начислено **{reward} голды**!")
    conn.close()

@dp.message(F.text == "👥 Рефералка")
async def referral_menu(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    user_data = get_user_data(user_id)
    await message.answer(f"🔗 Ссылка: `https://t.me/{bot_info.username}?start={user_id}`\n👥 Друзей: {user_data['referrals_count']}")

@dp.message(F.text == "💰 Вывод голды")
async def withdraw_gold(message: types.Message):
    if not await check_subscription(message.from_user.id): return
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data['balance'] < 50 or user_data['referrals_count'] < 5:
        await message.answer("❌ Нужно минимум 50 голды и 5 рефералов!")
    else:
        await message.answer("✅ Введите ваш ID в Standoff 2:")

@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    await message.answer(f"🛠 Саппорт: {SUPPORT_USERNAME}")

@dp.message(lambda message: message.text and message.text.startswith('/send_all'))
async def admin_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.replace('/send_all', '').strip()
    if not text: return
    for u_id in get_all_users():
        try: await bot.send_message(chat_id=u_id, text=text)
        except: pass

async def main(): await dp.start_polling(bot)
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
