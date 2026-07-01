import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import json

# ================= НАСТРОЙКА БОТА =================
TOKEN = '8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw'
WEBAPP_URL = "https://ten607-netizen.github.io/so2_naipex/"

# Твой личный Telegram ID (зашит намертво, никто другой не сможет использовать команды)
ADMIN_ID = 5376742900  

bot = telebot.TeleBot(TOKEN)

# База данных игроков и промокодов (хранится в памяти для стабильности на Railway)
USERS_DB = {}
PROMO_CODES = {
    "START": 100
}

# Регистрация пользователя в оперативной памяти
def register_user(user):
    uid = str(user.id)
    if uid not in USERS_DB:
        USERS_DB[uid] = {
            "name": user.first_name if user.first_name else "Игрок",
            "balance": 0,
            "inventory_count": 0
        }
    return USERS_DB[uid]

# --- ГЛАВНОЕ МЕНЮ (ОДИНАКОВОЕ ДЛЯ ВСЕХ, БЕЗ КНОПКИ АДМИНА) ---
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    web_app = WebAppInfo(url=WEBAPP_URL)
    btn_shop = KeyboardButton("🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ 🎰", web_app=web_app)
    
    btn_balance = KeyboardButton("💰 Мой Баланс")
    btn_withdraw = KeyboardButton("📤 Вывод голды")
    btn_ref = KeyboardButton("👥 Рефералы")
    btn_promo = KeyboardButton("🎁 Промокод")
    btn_top = KeyboardButton("🏆 Топ игроков")
    btn_help = KeyboardButton("ℹ️ Помощь / Правила")
    
    markup.add(btn_shop)
    markup.add(btn_balance, btn_withdraw)
    markup.add(btn_ref, btn_promo)
    markup.add(btn_top, btn_help)
        
    return markup


# ================= КОМАНДА /START =================
@bot.message_handler(commands=['start'])
def start_command(message):
    register_user(message.from_user)
    
    welcome_text = (
        f"🔥 *Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!* 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 *StandHub* — это лучший силятор открытия кейсов из Standoff 2 прямо в Telegram!\n\n"
        f"⚡️ Испытай свою удачу, крути рулетку, выбивай Арканы и собирай самый дорогой инвентарь!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *Все управление находится в кнопках ниже:* 👇"
    )
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= СЕКРЕТНАЯ КОМАНДА АДМИНА: /admin =================
@bot.message_handler(commands=['admin'])
def admin_panel_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return  # Обычные юзеры даже ответа не получат

    total_users = len(USERS_DB)
    total_promos = len(PROMO_CODES)
    
    admin_text = (
        f"👑 *ПАНЕЛЬ АДМИНИСТРАТОРА STANDHUB* 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *АКТУАЛЬНАЯ СТАТИСТИКА:*\n"
        f"🟢 Статус сервера: `ONLINE` (Railway)\n"
        f"👥 Игроков в текущей сессии: `{total_users} чел.`\n"
        f"🎁 Активных промокодов: `{total_promos} шт.`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 *Команда для создания промокода:*\n"
        f"`/create_promo НАЗВАНИЕ СУММА`\n"
        f"_(Пример: /create_promo NEWYEAR 500)_\n\n"
        f"📝 *Список кодов:* " + ", ".join([f"`{c}`" for c in PROMO_CODES.keys()])
    )
    bot.send_message(message.chat.id, admin_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= КОМАНДА АДМИНА: СОЗДАНИЕ ПРОМОКОДА =================
@bot.message_handler(commands=['create_promo'])
def create_promo_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Пиши команду так:\n`/create_promo ИМЯ СУММА`", parse_mode="Markdown")
        return

    promo_name = args[1].upper()
    try:
        promo_amount = int(args[2])
    except ValueError:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Сумма голды должна быть числом!", parse_mode="Markdown")
        return

    PROMO_CODES[promo_name] = promo_amount
    bot.send_message(message.chat.id, f"✅ *Успешно!* Создан промокод `{promo_name}` на *{promo_amount} Голды*!", reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= КОМАНДА ДЛЯ ИГРОКОВ: АКТИВАЦИЯ ПРОМОКОДОВ =================
@bot.message_handler(commands=['promo'])
def activate_promo(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Введи промокод! Например: `/promo START`", parse_mode="Markdown")
        return
        
    user_promo = args[1].upper()
    
    if user_promo in PROMO_CODES:
        gold_reward = PROMO_CODES[user_promo]
        
        # Начисляем голду
        u_data = register_user(message.from_user)
        u_data['balance'] += gold_reward
            
        bot.send_message(message.chat.id, f"🎉 *Успех!* Промокод `{user_promo}` активирован! Тебе начислено *+{gold_reward} Голды*! 🪙", reply_markup=get_main_menu(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Такого промокода не существует.", reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= ОБРАБОТКА ТЕКСТОВЫХ КНОПОК МЕНЮ =================
@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    chat_id = message.chat.id
    user_data = register_user(message.from_user)
    
    if message.text == "💰 Мой Баланс":
        balance_text = (
            f"💰 *ВАШ БАЛАНС* 💰\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 *Доступно для игры:* `{user_data['balance']} Голды` 🪙\n"
            f"🎒 *Ваш инвентарь:* `{user_data['inventory_count']} предметов`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Пополняйте баланс или активируйте промокоды!"
        )
        bot.send_message(chat_id, balance_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "📤 Вывод голды":
        withdraw_text = (
            f"📤 *ВЫВОД ГОЛДЫ В STANDOFF 2* 📤\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ℹ️ Вывод доступен от *50 Голды*.\n\n"
            f"📌 *Инструкция по выводу:*\n"
            f"1. Выставите любой дешевый предмет на рынок за сумму вывода.\n"
            f"2. Передайте ID предмета администрации.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ У вас пока недостаточно голды для оформления вывода."
        )
        bot.send_message(chat_id, withdraw_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "ℹ️ Помощь / Правила":
        help_text = (
            f"ℹ️ *ПОНЯТНАЯ ИНСТРУКЦИЯ ДЛЯ ИГРОКОВ* ℹ️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ Нажми кнопку *🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ* ниже.\n"
            f"2️⃣ Кликни на любой доступный кейс.\n"
            f"3️⃣ Нажми кнопку *🚀 ИСПЫТАТЬ УДАЧУ*, чтобы запустить рулетку.\n"
            f"4️⃣ Результат прилетит сюда!"
        )
        bot.send_message(chat_id, help_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "👥 Рефералы":
        bot_username = bot.get_me().username
        ref_text = (
            f"👥 *РЕФЕРАЛЬНАЯ СИСТЕМА* 👥\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 *Ваша ссылка для друзей:*\n"
            f"https://t.me/{bot_username}?start={chat_id}"
        )
        bot.send_message(chat_id, ref_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "🎁 Промокод":
        promo_text = (
            f"🎁 *АКТИВАЦИЯ ПРОМОКОДА* 🎁\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Чтобы активировать код, отправь сообщение в формате:\n"
            f"`/promo НАЗВАНИЕ_ПРОМОКОДА`"
        )
        bot.send_message(chat_id, promo_text, reply_markup=get_main_menu(), parse_mode="Markdown")

    elif message.text == "🏆 Топ игроков":
        # Сортировка по балансу в реальном времени
        sorted_users = sorted(USERS_DB.items(), key=lambda x: x[1]['balance'], reverse=True)
        
        top_text = f"🏆 *НАСТОЯЩИЙ ТОП ИГРОКОВ STANDHUB* 🏆\n"
        top_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
        for i in range(5):
            if i < len(sorted_users):
                u_info = sorted_users[i][1]
                top_text += f"{medals[i]} {i+1}. `{u_info['name']}` — {u_info['balance']} Голды 🪙\n"
            else:
                top_text += f"{medals[i]} {i+1}. `Свободное место` — 0 Голды 🪙\n"
                
        top_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.send_message(chat_id, top_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= ПРИЕМ ДРОПА ИЗ РУЛЕТКИ (WEBAPP) =================
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        item_name = data.get("item_name", "Неизвестный предмет")
        item_price = data.get("item_price", 0)
        
        u_data = register_user(message.from_user)
        u_data['inventory_count'] += 1
        
        drop_text = (
            f"🎉 *ПОЗДРАВЛЯЕМ! ТЕБЕ ВЫПАЛ ДРОП!* 🎉\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔫 *Твоя награда:* ✨ *{item_name}* ✨\n"
            f"💰 *Цена на рынке:* `{item_price} Голды` 🪙\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 Скин сохранен в инвентарь!"
        )
        bot.send_message(message.chat.id, drop_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка сохранения предмета.", reply_markup=get_main_menu(), parse_mode="Markdown")


if __name__ == '__main__':
    print("[OK] Кнопка админа удалена. Все команды админа доступны строго по текстовому запросу.")
    bot.polling(none_stop=True)
