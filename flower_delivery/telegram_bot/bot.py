import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command  # Фильтр для команд
from .bot_config import BOT_TOKEN

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="📦 Мои заказы")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Добро пожаловать в Flower Delivery Bot!\nВыберите действие:", reply_markup=menu)

# Получение списка товаров через API
@dp.message(F.text == "🛍 Каталог")  # Новый способ фильтрации текста
async def catalog(message: types.Message):
    response = requests.get("http://127.0.0.1:8000/api/orders/")  # Запрос к API
    if response.status_code == 200:
        orders = response.json()
        if not orders:
            await message.answer("❌ Каталог пуст!")
        else:
            text = "🌸 **Наши товары:**\n\n"
            for item in orders:
                text += f"🔹 *{item['products'][0]['name']}* - {item['products'][0]['price']} ₽\n"
            await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Ошибка загрузки каталога!")

# Запуск бота с asyncio
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(dp)  # Подключаем маршруты
    await dp.start_polling(bot)

# Функция для Django
def start_bot():
    asyncio.run(main())  # Запускаем бота через asyncio
