import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import json

# ================= НАСТРОЙКА БОТА =================
TOKEN = '8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw'
WEBAPP_URL = "https://ten607-netizen.github.io/so2_naipex/"

# Твой личный Telegram ID для доступа к админке
ADMIN_ID = 5376742900  

bot = telebot.TeleBot(TOKEN)

# База данных промокодов в оперативной памяти
# Формат: {"НАЗВАНИЕ": сумма_голды}
PROMO_CODES = {
    "START": 100
}

# --- ГЛАВНОЕ МЕНЮ (ДЛЯ ИГРОКОВ И АДМИНА) ---
def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Главная кнопка WebApp на всю ширину
    web_app = WebAppInfo(url=WEBAPP_URL)
    btn_shop = KeyboardButton("🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ 🎰", web_app=web_app)
    
    btn_balance = KeyboardButton("💰 Мой Баланс")
    btn_withdraw = KeyboardButton("📤 Вывод голды")
    btn_ref = KeyboardButton("👥 Рефералы")
    btn_promo = KeyboardButton("🎁 Промокод")
    btn_help = KeyboardButton("ℹ️ Помощь / Правила")
    
    markup.add(btn_shop)
    markup.add(btn_balance, btn_withdraw)
    markup.add(btn_ref, btn_promo)
    markup.add(btn_help)
    
    # Кнопка админа — строго для твоего аккаунта
    if user_id == ADMIN_ID:
        btn_admin = KeyboardButton("👑 Админ-панель")
        markup.add(btn_admin)
        
    return markup


# ================= КОМАНДА /START =================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"🔥 *Привет, {user_name}! Добро пожаловать в StandHub!* 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 *StandHub* — это лучший симулятор открытия кейсов из Standoff 2 прямо в Telegram!\n\n"
        f"⚡️ Испытай свою удачу, крути рулетку, выбивай Арканы и собирай самый дорогой инвентарь!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *Все управление находится в кнопках ниже:* 👇"
    )
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=get_main_menu(user_id), 
        parse_mode="Markdown"
    )


# ================= ОБРАБОТКА ТЕКСТОВЫХ КНОПОК МЕНЮ =================
@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Кнопка: Мой Баланс
    if message.text == "💰 Мой Баланс":
        balance_text = (
            f"💰 *ВАШ БАЛАНС* 💰\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 *Доступно для игры:* `0 Голды` 🪙\n"
            f"🎒 *Ваш инвентарь:* `0 предметов`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Пополняйте баланс у администратора или приглашайте друзей!"
        )
        bot.send_message(chat_id, balance_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")
        
    # Кнопка: Вывод голды
    elif message.text == "📤 Вывод голды":
        withdraw_text = (
            f"📤 *ВЫВОД ГОЛДЫ В STANDOFF 2* 📤\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ℹ️ Вывод доступен от *50 Голды*.\n\n"
            f"📌 *Инструкция по выводу:*\n"
            f"1. Выставите любой дешевый предмет на рынок Standoff 2 за сумму вывода.\n"
            f"2. Передайте ID выставленного предмета и ваш игровой ник тех. поддержке.\n"
            f"3. Ожидайте покупку скина в течение 24 часов.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ У вас пока недостаточно голды для оформления вывода."
        )
        bot.send_message(chat_id, withdraw_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")
        
    # Кнопка: Помощь / Правила
    elif message.text == "ℹ️ Помощь / Правила":
        help_text = (
            f"ℹ️ *ПОНЯТНАЯ ИНСТРУКЦИЯ ДЛЯ ИГРОКОВ* ℹ️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ Нажми кнопку *🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ* ниже.\n"
            f"2️⃣ Кликни на любой доступный кейс.\n"
            f"3️⃣ Нажми кнопку *🚀 ИСПЫТАТЬ УДАЧУ*, чтобы запустить рулетку.\n"
            f"4️⃣ После остановки рулетки твой выигрыш мгновенно прилетит сообщением прямо сюда!"
        )
        bot.send_message(chat_id, help_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")
        
    # Кнопка: Рефералы
    elif message.text == "👥 Рефералы":
        bot_username = bot.get_me().username
        ref_text = (
            f"👥 *РЕФЕРАЛЬНАЯ СИСТЕМА* 👥\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 *Ваша персональная ссылка для друзей:*\n"
            f"https://t.me/{bot_username}?start={chat_id}\n\n"
            f"🎁 Отправляй её друзьям и получай бонусы за каждого, кто запустит бота!\n"
            f"📈 Всего приглашено: `0` человек."
        )
        bot.send_message(chat_id, ref_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")
        
    # Кнопка: Промокод
    elif message.text == "🎁 Промокод":
        promo_text = (
            f"🎁 *АКТИВАЦИЯ ПРОМОКОДА* 🎁\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Чтобы активировать промокод на голду, отправь его в чат в формате:\n"
            f"`/promo НАЗВАНИЕ_ПРОМОКОДА`\n\n"
            f"📢 Ищи секретные коды в нашем официальном канале!"
        )
        bot.send_message(chat_id, promo_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")

    # Кнопка: ЛИЧНАЯ АДМИН-ПАНЕЛЬ
    elif message.text == "👑 Админ-панель" and user_id == ADMIN_ID:
        admin_text = (
            f"👑 *ПАНЕЛЬ РАЗРАБОТЧИКА STANDHUB* 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛠 *Управление промокодами:*\n"
            f"➕ Чтобы создать новый промокод, отправь в чат команду:\n"
            f"`/create_promo НАЗВАНИЕ СУММА`\n"
            f"_(Пример: /create_promo UPDATE500 500)_\n\n"
            f"📝 *Активные промокоды в базе сейчас:*\n"
        )
        for code, amount in PROMO_CODES.items():
            admin_text += f"• `{code}` — на {amount} Голды\n"
            
        bot.send_message(chat_id, admin_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")


# ================= КОМАНДА АДМИНА: СОЗДАНИЕ ПРОМОКОДА =================
@bot.message_handler(commands=['create_promo'])
def create_promo_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Неверный формат! Пиши так:\n`/create_promo ИМЯ_КОДА СУММА`", parse_mode="Markdown")
        return

    promo_name = args[1].upper()
    try:
        promo_amount = int(args[2])
    except ValueError:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Сумма голды должна быть числом!", parse_mode="Markdown")
        return

    # Сохраняем промокод в словарь
    PROMO_CODES[promo_name] = promo_amount
    bot.send_message(
        message.chat.id, 
        f"✅ *Успешно!* Создан промокод `{promo_name}` на *{promo_amount} Голды*!", 
        reply_markup=get_main_menu(user_id), 
        parse_mode="Markdown"
    )


# ================= КОМАНДА ДЛЯ ИГРОКОВ: АКТИВАЦИЯ ПРОМОКОДОВ =================
@bot.message_handler(commands=['promo'])
def activate_promo(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Введи промокод! Например: `/promo START`", parse_mode="Markdown")
        return
        
    user_promo = args[1].upper()
    
    # Проверка промокода
    if user_promo in PROMO_CODES:
        gold_reward = PROMO_CODES[user_promo]
        bot.send_message(
            message.chat.id, 
            f"🎉 *Успех!* Промокод `{user_promo}` активирован! Тебе начислено *+{gold_reward} Голды*! 🪙", 
            reply_markup=get_main_menu(user_id),
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Такого промокода не существует.", reply_markup=get_main_menu(user_id), parse_mode="Markdown")


# ================= ПРИЕМ ДРОПА ИЗ РУЛЕТКИ (WEBAPP) =================
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    user_id = message.from_user.id
    try:
        data = json.loads(message.web_app_data.data)
        item_name = data.get("item_name", "Неизвестный предмет")
        item_price = data.get("item_price", 0)
        case_cost = data.get("case_cost", 100)
        
        drop_text = (
            f"🎉 *ПОЗДРАВЛЯЕМ! ТЕБЕ ВЫПАЛ ДРОП!* 🎉\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 *Открыт кейс:* `Fire Case` (за {case_cost} Голды)\n"
            f"🔫 *Твоя награда:* ✨ *{item_name}* ✨\n"
            f"💰 *Цена на рынке:* `{item_price} Голды` 🪙\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 Скин сохранен в твой инвентарь! Можешь копить на вывод или продать!"
        )
        
        bot.send_message(message.chat.id, drop_text, reply_markup=get_main_menu(user_id), parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ _Произошла ошибка при сохранении предмета._", reply_markup=get_main_menu(user_id), parse_mode="Markdown")


# ================= ЗАПУСК БОТА =================
if __name__ == '__main__':
    print("[OK] Бот запущен! Кнопка админа привязана к твоему ID.")
    bot.polling(none_stop=True)
