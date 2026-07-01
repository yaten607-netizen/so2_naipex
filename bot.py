import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import json

# ================= НАСТРОЙКА БОТА =================
TOKEN = '8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw'
WEBAPP_URL = "https://ten607-netizen.github.io/so2_naipex/"

# Твой личный Telegram ID
ADMIN_ID = 5376742900  

# Юзернейм твоего канала
CHANNEL_USERNAME = "@standhub_channel" 

bot = telebot.TeleBot(TOKEN)

# База данных игроков в оперативной памяти
USERS_DB = {}

# База данных промокодов
PROMO_CODES = {
    "START": {
        "gold": 100,
        "uses": 99999,
        "users_activated": []
    }
}

# Регистрация пользователя
def register_user(user):
    uid = str(user.id)
    if uid not in USERS_DB:
        USERS_DB[uid] = {
            "name": user.first_name if user.first_name else "Игрок",
            "balance": 0,
            "inventory_count": 0
        }
    return USERS_DB[uid]

# Проверка подписки на канал
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return True

# --- ГЛАВНОЕ МЕНЮ ---
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
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        btn_link = InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        btn_check = InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")
        markup.add(btn_link)
        markup.add(btn_check)
        
        bot.send_message(
            message.chat.id, 
            "⚠️ *Доступ ограничен!*\n\nЧтобы играть в StandHub и открывать кейсы, ты должен быть подписан на наш официальный канал!", 
            reply_markup=markup, 
            parse_mode="Markdown"
        )
        return

    register_user(message.from_user)
    
    welcome_text = (
        f"🔥 *Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!* 🔥\n"
        f"----------------------------------------\n"
        f"🌟 *StandHub* — это лучший симулятор открытия кейсов из Standoff 2 прямо в Telegram!\n\n"
        f"⚡️ Испытай свою удачу, крути рулетку, выбивай Арканы и собирай самый дорогой инвентарь!\n"
        f"----------------------------------------\n"
        f"👇 *Все управление находится в кнопках ниже:* 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= ОБРАБОТКА ИНЛАЙН-КНОПКИ ПРОВЕРКИ ПОДПИСКИ =================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        register_user(call.from_user)
        bot.answer_callback_query(call.id, "🎉 Успешно! Доступ открыт.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        welcome_text = (
            f"🔥 *Добро пожаловать в StandHub!* 🔥\n"
            f"----------------------------------------\n"
            f"👇 *Все управление находится в кнопках ниже:* 👇"
        )
        bot.send_message(call.message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "❌ Ты всё ещё не подписался на канал!", show_alert=True)


# ================= КОМАНДА АДМИНА: /admin =================
@bot.message_handler(commands=['admin'])
def admin_panel_command(message):
    if message.from_user.id != ADMIN_ID:
        return

    total_users = len(USERS_DB)
    total_promos = len(PROMO_CODES)
    
    admin_text = (
        f"👑 *ПАНЕЛЬ АДМИНИСТРАТОРА STANDHUB* 👑\n"
        f"----------------------------------------\n"
        f"📊 *АКТУАЛЬНАЯ СТАТИСТИКА:*\n"
        f"🟢 Статус сервера: `ONLINE`\n"
        f"👥 Игроков в сессии: `{total_users} чел.`\n"
        f"🎁 Промокодов создано: `{total_promos} шт.`\n"
        f"----------------------------------------\n"
        f"🛠 *КОМАНДЫ УПРАВЛЕНИЯ:*\n"
        f"➕ Создать лимитированный промокод:\n`/create_promo НАЗВАНИЕ ГОЛДА АКТИВАЦИИ`\n"
        f"_(Пример: /create_promo BOOST500 500 10)_\n\n"
        f"📢 Рассылка всем игрокам:\n`/send ТЕКСТ РАССЫЛКИ`\n\n"
        f"📝 *Список кодов в базе:*\n"
    )
    for code, data in PROMO_CODES.items():
        admin_text += f"• `{code}` — {data['gold']} голды (Осталось: {data['uses']} акт.)\n"

    bot.send_message(message.chat.id, admin_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= КОМАНДА АДМИНА: /create_promo =================
@bot.message_handler(commands=['create_promo'])
def create_promo_command(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 4:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Мало данных! Пиши строго так:\n`/create_promo НАЗВАНИЕ ГОЛДА АКТИВАЦИИ`", parse_mode="Markdown")
        return

    promo_name = args[1].upper()
    try:
        promo_amount = int(args[2])
        promo_uses = int(args[3])
    except ValueError:
        bot.send_message(message.chat.id, "❌ *Ошибка:* И голда, и число активаций должны быть числами!", parse_mode="Markdown")
        return

    PROMO_CODES[promo_name] = {
        "gold": promo_amount,
        "uses": promo_uses,
        "users_activated": []
    }
    
    bot.send_message(
        message.chat.id, 
        f"✅ *Промокод успешно создан!*\n\n"
        f"📋 Название: `{promo_name}`\n"
        f"🪙 Награда: `+{promo_amount} Голды`\n"
        f"👥 Лимит: `{promo_uses}` человек.", 
        reply_markup=get_main_menu(), 
        parse_mode="Markdown"
    )


# ================= КОМАНДА АДМИНА: /send (ОБЩАЯ РАССЫЛКА) =================
@bot.message_handler(commands=['send'])
def admin_send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    broadcast_text = message.text[5:].strip()
    
    if not broadcast_text:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Вы не ввели текст для рассылки! Пример:\n`/send Всем привет!`", parse_mode="Markdown")
        return

    if len(USERS_DB) == 0:
        bot.send_message(message.chat.id, "❌ *Ошибка:* База данных пуста.", parse_mode="Markdown")
        return

    success_count = 0
    for uid in USERS_DB.keys():
        try:
            bot.send_message(int(uid), broadcast_text, parse_mode="Markdown")
            success_count += 1
        except Exception as e:
            print(f"Не удалось отправить пользователю {uid}: {e}")

    bot.send_message(message.chat.id, f"📢 *Рассылка завершена!*\nУспешно отправлено: `{success_count}` из `{len(USERS_DB)}` игроков.", parse_mode="Markdown")


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
        promo_data = PROMO_CODES[user_promo]
        
        if user_id in promo_data["users_activated"]:
            bot.send_message(message.chat.id, "❌ *Ошибка:* Ты уже активировал данный промокод!", reply_markup=get_main_menu(), parse_mode="Markdown")
            return
            
        if promo_data["uses"] <= 0:
            bot.send_message(message.chat.id, "❌ *Ошибка:* Этот промокод закончился!", reply_markup=get_main_menu(), parse_mode="Markdown")
            return
            
        gold_reward = promo_data["gold"]
        u_data = register_user(message.from_user)
        u_data['balance'] += gold_reward
        
        promo_data["uses"] -= 1
        promo_data["users_activated"].append(user_id)
            
        bot.send_message(
            message.chat.id, 
            f"🎉 *Успех!* Промокод `{user_promo}` активирован!\n🪙 Тебе начислено: *+{gold_reward} Голды!*\n"
            f"📥 _Осталось активаций этого кода:_ `{promo_data['uses']}`", 
            reply_markup=get_main_menu(), 
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Такого промокода не существует.", reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= ОБРАБОТКА ТЕКСТОВЫХ КНОПОК МЕНЮ (СТРОГО ВНИЗУ) =================
@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        bot.send_message(chat_id, "⚠️ Вы не подписаны на канал. Нажмите `/start` для проверки подписки.")
        return

    user_data = register_user(message.from_user)
    
    if message.text == "💰 Мой Баланс":
        balance_text = (
            f"💰 *ВАШ БАЛАНС* 💰\n"
            f"----------------------------------------\n"
            f"💵 *Доступно для игры:* `{user_data['balance']} Голды` 🪙\n"
            f"🎒 *Ваш инвентарь:* `{user_data['inventory_count']} предметов`\n"
            f"----------------------------------------\n"
            f"Пополняйте баланс или активируйте промокоды!"
        )
        bot.send_message(chat_id, balance_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "📤 Вывод голды":
        withdraw_text = (
            f"📤 *ВЫВОД ГОЛДЫ В STANDOFF 2* 📤\n"
            f"----------------------------------------\n"
            f"ℹ️ Вывод доступен от *50 Голды*.\n\n"
            f"📌 *Инструкция по выводу:*\n"
            f"1. Выставите любой дешевый предмет на рынок за сумму вывода.\n"
            f"2. Передайте ID предмета администрации.\n"
            f"----------------------------------------\n"
            f"❌ У вас пока недостаточно голды для оформления вывода."
        )
        bot.send_message(chat_id, withdraw_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "ℹ️ Помощь / Правила":
        help_text = (
            f"ℹ️ *ПОНЯТНАЯ ИНСТРУКЦИЯ ДЛЯ ИГРОКОВ* ℹ️\n"
            f"----------------------------------------\n"
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
            f"----------------------------------------\n"
            f"🔗 *Ваша ссылка для друзей:*\n"
            f"https://t.me/{bot_username}?start={chat_id}"
        )
        bot.send_message(chat_id, ref_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif message.text == "🎁 Промокод":
        promo_text = (
            f"🎁 *АКТИВАЦИЯ ПРОМОКОДА* 🎁\n"
            f"----------------------------------------\n"
            f"👉 Чтобы активировать код, отправь сообщение в формате:\n"
            f"`/promo НАЗВАНИЕ_ПРОМОКОДА`"
        )
        bot.send_message(chat_id, promo_text, reply_markup=get_main_menu(), parse_mode="Markdown")

    elif message.text == "🏆 Топ игроков":
        sorted_users = sorted(USERS_DB.items(), key=lambda x: x[1]['balance'], reverse=True)
        top_text = f"🏆 *НАСТОЯЩИЙ ТОП ИГРОКОВ STANDHUB* 🏆\n"
        top_text += f"----------------------------------------\n"
        
        medals = ["1.", "2.", "3.", "4.", "5."]
        for i in range(5):
            if i < len(sorted_users):
                u_info = sorted_users[i][1]
                top_text += f"{medals[i]} `{u_info['name']}` — {u_info['balance']} Голды 🪙\n"
            else:
                top_text += f"{medals[i]} `Свободное место` — 0 Голды 🪙\n"
                
        top_text += f"----------------------------------------\n"
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
            f"----------------------------------------\n"
            f"🔫 *Твоя награда:* {item_name}\n"
            f"💰 *Цена на рынке:* `{item_price} Голды` 🪙\n"
            f"----------------------------------------\n"
            f"🔥 Скин сохранен в инвенварь!"
        )
        bot.send_message(message.chat.id, drop_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка сохранения предмета.", reply_markup=get_main_menu(), parse_mode="Markdown")


if __name__ == '__main__':
    bot.polling(none_stop=True)
