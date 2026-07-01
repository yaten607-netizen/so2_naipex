import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import json

# ================= НАСТРОЙКА БОТА =================
TOKEN = 'ТВОЙ_ТОКЕН_БОТА'
WEBAPP_URL = "https://ТВОЙ_НИК.github.io/so2_naipex/"

bot = telebot.TeleBot(TOKEN)

# --- ГЛАВНОЕ МЕНЮ (НИЖНИЕ КНОПКИ) ---
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    # Главная кнопка-запускалка
    web_app = WebAppInfo(url=WEBAPP_URL)
    btn_shop = KeyboardButton("🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ 🎰", web_app=web_app)
    markup.add(btn_shop)
    return markup

# --- КРАСИВЫЕ ИНЛАЙН-КНОПКИ ПОД СООБЩЕНИЕМ /START ---
def get_start_inline():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_profile = InlineKeyboardButton("👤 Мой Профиль", callback_data="open_profile")
    btn_help = InlineKeyboardButton("ℹ️ Помощь и Правила", callback_data="open_help")
    markup.add(btn_profile, btn_help)
    return markup

# --- КНОПКА НАЗАД ДЛЯ ИНЛАЙН-МЕНЮ ---
def get_back_inline():
    markup = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton("⬅️ Вернуться в меню", callback_data="back_to_start")
    markup.add(btn_back)
    return markup


# ================= КОМАНДА /START =================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"🔥 *Привет, {user_name}! Добро пожаловать в StandHub!* 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 *StandHub* — это продвинутый симулятор открытия кейсов из Standoff 2 прямо внутри Telegram!\n\n"
        f"⚡️ Испытай свою удачу, крути рулетку, выбивай Арканы и собирай самый дорогой инвентарь!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *Используй понятное меню ниже для управления:* 👇"
    )
    
    # Отправляем сообщение с инлайн-кнопками профиля и помощи
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=get_start_inline(), 
        parse_mode="Markdown"
    )
    # Выкатываем нижнюю кнопку магазина, чтобы она закрепилась
    bot.send_message(
        message.chat.id,
        "🎒 Чтобы перейти к выбору кейсов, нажми большую кнопку «*ОТКРЫТЬ МАГАЗИН КЕЙСОВ*» в самом низу.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


# ================= ОБРАБОТКА НАЖАТИЙ НА КНОПКИ (CALLBACK) =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    # Логика для кнопки "Мой Профиль"
    if call.data == "open_profile":
        profile_text = (
            f"👤 *ВАШ ИГРОВОЙ ПРОФИЛЬ* 👤\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Имя игрока:* {call.from_user.first_name}\n"
            f"🆔 *Ваш ID:* `{call.message.chat.id}`\n\n"
            f"💰 *Текущий баланс:* `1,000 Голды` 🪙\n"
            f"🎒 *Предметов в инвентаре:* `0 шт.`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 _Баланс уже зачислен! Заходи в магазин и выбивай скины!_"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=profile_text,
            reply_markup=get_back_inline(),
            parse_mode="Markdown"
        )
        
    # Логика для кнопки "Помощь и Правила"
    elif call.data == "open_help":
        help_text = (
            f"ℹ️ *ИНСТРУКЦИЯ ДЛЯ ИГРОКОВ* ℹ️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 *Как устроен процесс?*\n"
            f"1️⃣ Нажми кнопку *🎰 ОТКРЫТЬ МАГАЗИН КЕЙСОВ* в самом низу экрана.\n"
            f"2️⃣ В открывшемся окне выбери кейс.\n"
            f"3️⃣ Нажми кнопку *🚀 ИСПЫТАТЬ УДАЧУ*, чтобы запустить рулетку.\n"
            f"4️⃣ После остановки рулетки твой выигрыш мгновенно прилетит сообщением прямо сюда!\n\n"
            f"💎 *Где взять баланс?*\n"
            f"Каждому новому пользователю мы дарим стартовые *1,000 Голды*!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 _Удачи в открытии! Пусть тебе повезет на Gold или Arcana!_"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=help_text,
            reply_markup=get_back_inline(),
            parse_mode="Markdown"
        )
        
    # Возврат назад в главное меню
    elif call.data == "back_to_start":
        user_name = call.from_user.first_name
        welcome_text = (
            f"🔥 *Привет, {user_name}! Добро пожаловать в StandHub!* 🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌟 *StandHub* — это продвинутый симулятор открытия кейсов из Standoff 2 прямо внутри Telegram!\n\n"
            f"⚡️ Испытай свою удачу, крути рулетку, выбивай Арканы и собирай самый дорогой инвентарь!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 *Используй понятное меню ниже для управления:* 👇"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=welcome_text,
            reply_markup=get_start_inline(),
            parse_mode="Markdown"
        )


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
            f"🔥 Скин сохранен в твой инвентарь! Крути еще, кнопка внизу!"
        )
        
        bot.send_message(
            message.chat.id, 
            drop_text, 
            reply_markup=get_main_menu(), 
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id, 
            "❌ _Произошла ошибка при сохранении предмета. Попробуй еще раз!_",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

# ================= ЗАПУСК СЛУШАТЕЛЯ =================
if __name__ == '__main__':
    print("[OK] Бот успешно запущен и готов встречать игроков!")
    bot.polling(none_stop=True)
