import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import json

# ================= НАСТРОЙКА БОТА =================
TOKEN = '8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw'
# Ссылка на твой WebApp-магазин
WEBAPP_URL = "https://ten607-netizen.github.io/so2_naipex/"

bot = telebot.TeleBot(TOKEN)

# --- ГЛАВНОЕ МЕНЮ (ВСЕ КНОПКИ СНИЗУ) ---
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # 1. Главная кнопка на всю ширину — Магазин
    web_app = WebAppInfo(url=WEBAPP_URL)
    btn_shop = KeyboardButton("🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ 🎰", web_app=web_app)
    
    # 2. Остальные кнопки управления
    btn_balance = KeyboardButton("💰 Мой Баланс")
    btn_help = KeyboardButton("ℹ️ Помощь / Правила")
    btn_ref = KeyboardButton("👥 Рефералы")
    btn_promo = KeyboardButton("🎁 Промокод")
    
    # Собираем меню
    markup.add(btn_shop)
    markup.add(btn_balance, btn_help)
    markup.add(btn_ref, btn_promo)
    return markup


# ================= КОМАНДА /START =================
@bot.message_handler(commands=['start'])
def start_command(message):
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
        reply_markup=get_main_menu(), 
        parse_mode="Markdown"
    )


# ================= ОБРАБОТКА ТЕКСТОВЫХ КНОПОК МЕНЮ =================
@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    chat_id = message.chat.id
    
    # Кнопка: Мой Баланс
    if message.text == "💰 Мой Баланс":
        balance_text = (
            f"💰 *ВАШ БАЛАНС* 💰\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 *Текущий счет:* `1,000 Голды` 🪙\n"
            f"🎒 *Ваш инвентарь:* `0 предметов`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 _Стартовый баланс зачислен! Скорее открывай кейсы!_"
        )
        bot.send_message(chat_id, balance_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    # Кнопка: Помощь / Правила
    elif message.text == "ℹ️ Помощь / Правила":
        help_text = (
            f"ℹ️ *ПОНЯТНАЯ ИНСТРУКЦИЯ ДЛЯ ИГРОКОВ* ℹ️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ Нажми кнопку *🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ* ниже.\n"
            f"2️⃣ Кликни на любой доступный кейс.\n"
            f"3️⃣ Нажми кнопку *🚀 ИСПЫТАТЬ УДАЧУ*, чтобы запустить рулетку.\n"
            f"4️⃣ После остановки рулетки твой выигрыш мгновенно прилетит сообщением прямо сюда!\n\n"
            f"💎 Всем новичкам при старте уже выдано *1,000 Голды*!"
        )
        bot.send_message(chat_id, help_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    # Кнопка: Рефералы
    elif message.text == "👥 Рефералы":
        ref_text = (
            f"👥 *РЕФЕРАЛЬНАЯ СИСТЕМА* 👥\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 *Ваша ссылка для приглашения друзей:*\n"
            f"https://t.me/ТВОЙ_БОТ?start={chat_id}\n\n"
            f"🎁 Приглашай друзей и получай по *+250 Голды* за каждого активного игрока!\n"
            f"📈 Всего приглашено: `0` человек."
        )
        bot.send_message(chat_id, ref_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    # Кнопка: Промокод
    elif message.text == "🎁 Промокод":
        promo_text = (
            f"🎁 *АКТИВАЦИЯ ПРОМОКОДА* 🎁\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Чтобы активировать промокод на голду, отправь его в чат в следующем формате:\n"
            f"`/promo ТВОЙ_ПРОМОКОД`\n\n"
            f"📢 Ищи секретные промокоды в нашем официальном канале!"
        )
        bot.send_message(chat_id, promo_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= КОМАНДА ДЛЯ АКТИВАЦИИ ПРОМОКОДОВ =================
@bot.message_handler(commands=['promo'])
def activate_promo(message):
    # Пример простой логики промокода
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Введи промокод! Например: `/promo START`", parse_mode="Markdown")
        return
        
    promo_code = args[1].upper()
    if promo_code == "START":
        bot.send_message(message.chat.id, "🎉 *Успех!* Промокод `START` активирован! Вам начислено *+500 Голды*! 🪙", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ *Ошибка:* Такого промокода не существует или у него истек срок действия.", parse_mode="Markdown")


# ================= ПРИЕМ ДРОПА ИЗ РУЛЕТКИ (WEBAPP) =================
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
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
            f"🔥 Скин сохранен в твой инвентарь!"
        )
        
        bot.send_message(message.chat.id, drop_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ _Произошла ошибка при сохранении предмета._", reply_markup=get_main_menu(), parse_mode="Markdown")


# ================= ЗАПУСК БОТА =================
if __name__ == '__main__':
    print("[OK] Бот успешно запущен со всеми нижними кнопками!")
    bot.polling(none_stop=True)
