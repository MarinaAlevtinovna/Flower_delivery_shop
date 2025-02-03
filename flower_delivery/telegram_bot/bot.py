import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import requests
from .bot_config import BOT_TOKEN

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Клавиатура
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("🛍 Каталог"), KeyboardButton("📦 Мои заказы"))

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("👋 Добро пожаловать в Flower Delivery Bot!\nВыберите действие:", reply_markup=menu)

# Получение списка товаров через API
@dp.message_handler(lambda message: message.text == "🛍 Каталог")
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

# Запуск бота
def start_bot():
    executor.start_polling(dp, skip_updates=True)
