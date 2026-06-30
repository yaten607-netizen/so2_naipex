import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Включаем логирование, чтобы видеть статус бота в консоли Railway
logging.basicConfig(level=logging.INFO)

# Твой рабочий токен
BOT_TOKEN = "8802875670:AAFIKoKmaRtmSh8wL32mMKkIiLObKYqSpTw"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция для создания главного меню с кнопками
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💰 Вывод голды")
    builder.button(text="🎁 Промокод")
    builder.button(text="❓ Помощь")
    builder.adjust(2, 1) # Две кнопки в первом ряду, одна во втором
    return builder.as_markup(resize_keyboard=True)

# 1. Обработка команды /start (Приветствие + информация про рефералку)
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в StandHub!\n\n"
        "👥 **Наша реферальная система:**\n"
        "Приглашай друзей по своей ссылке и получай бонусную голду за каждого активного реферала! "
        "Твою личную ссылку можно найти в профиле. Больше друзей — больше голды! 🔥"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu())

# 2. Кнопка "Вывод голды" (Ограничение от 50 голды)
@dp.message(F.text == "💰 Вывод голды")
async def withdraw_gold(message: types.Message):
    user_balance = 0 # Временный баланс (пока не подключена база данных)
    
    if user_balance < 50:
        await message.answer(
            f"❌ **Ошибка вывода**\n\n"
            f"Минимальная сумма для вывода составляет **50 голды**.\n"
            f"Ваш текущий баланс: {user_balance} голды.\n\n"
            f"Зарабатывайте голду, приглашая друзей или активируя промокоды!"
        )
    else:
        await message.answer("✅ Введите количество голды для вывода и укажите ваш ID в Standoff 2:")

# 3. Кнопка "Промокод"
@dp.message(F.text == "🎁 Промокод")
async def promo_code(message: types.Message):
    await message.answer(
        "🎟 **Активация промокода**\n\n"
        "Введите ваш промокод в ответ на это сообщение, чтобы получить голду или бонусы!"
    )

# 4. Кнопка "Помощь"
@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    help_text = (
        "🛠 **Поддержка и Помощь StandHub**\n\n"
        "• Как заработать? Приглашайте друзей или ловите промокоды в нашем канале!\n"
        "• Как вывести голду? Накопите 50 голды и нажмите кнопку 'Вывод голды'.\n\n"
        "📬 Если у вас возникли вопросы или нашли баг, пишите создателю бота."
    )
    await message.answer(help_text)

# Запуск процесса пуллинга
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())