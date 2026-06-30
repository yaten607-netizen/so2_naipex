import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Логи для Railway
logging.basicConfig(level=logging.INFO)

# Твой рабочий токен
BOT_TOKEN = "8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню (нижние кнопки)
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💰 Вывод голды")
    builder.button(text="🎁 Промокод")
    builder.button(text="👥 Рефералка")
    builder.button(text="❓ Помощь")
    
    # Кнопка для веб-приложения, которая теперь открывает кейсы!
    builder.button(
        text="🎰 Открыть Кейсы", 
        web_app=types.WebAppInfo(url="https://google.com") # Сюда потом вставим ссылку на твою вебку с кейсами
    )
    
    builder.adjust(2, 2, 1) # Разметка кнопок (2 в первом ряду, 2 во втором, кнопка кейсов на всю ширину внизу)
    return builder.as_markup(resize_keyboard=True)

# 1. Команда /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!\n\n"
        "Здесь ты можешь зарабатывать голду Standoff 2, приглашая друзей и активируя промокоды. "
        "А в меню ниже тебя ждут бесплатные кейсы с крутыми призами! 🔥"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu())

# 2. ОТДЕЛЬНАЯ КНОПКА: Рефералка (выдает ссылку текстом)
@dp.message(F.text == "👥 Рефералка")
async def referral_menu(message: types.Message):
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    my_referrals = 0 # Позже будет из базы данных
    
    ref_text = (
        "👥 **Реферальная система StandHub**\n\n"
        f"🔗 **Твоя ссылка для приглашений:**\n`{ref_link}`\n\n"
        f"📊 У тебя приглашено друзей: **{my_referrals}**\n\n"
        "За каждого друга ты получаешь голду! Напоминаем, что для вывода нужно пригласить минимум 5 друзей."
    )
    await message.answer(ref_text, parse_mode="Markdown")

# 3. Кнопка "Вывод голды" (Проверка: 50 голды И 5 рефералов)
@dp.message(F.text == "💰 Вывод голды")
async def withdraw_gold(message: types.Message):
    user_balance = 0 # Заглушка
    user_referrals = 0 # Заглушка
    
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
        await message.answer("✅ Отлично! Условия выполнены. Введите ваш ID в Standoff 2 для получения голды:")

# 4. Кнопка "Промокод"
@dp.message(F.text == "🎁 Промокод")
async def promo_code(message: types.Message):
    await message.answer("🎟 **Активация промокода**\n\nВведите ваш промокод в ответ на это сообщение:")

# 5. Кнопка "Помощь"
@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    help_text = (
        "🛠 **Поддержка StandHub**\n\n"
        "• Вывод: от 50 голды и 5 рефералов.\n"
        "• Кнопка 'Рефералка' даст тебе ссылку для друзей.\n"
        "• Кнопка '🎰 Открыть Кейсы' запустит игру прямо в Телеграм.\n\n"
        "📬 По всем вопросам пишите создателю бота."
    )
    await message.answer(help_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())