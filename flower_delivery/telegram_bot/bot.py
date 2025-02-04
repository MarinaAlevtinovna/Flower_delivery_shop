import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .bot_config import BOT_TOKEN, API_TOKEN, ADMIN_ID
import logging

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",  # Лог сохраняется в файл
    filemode="a",  # Дописывает в файл (не перезаписывает)
)

# Дополнительно выводим ошибки в консоль
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

# Клавиатура
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="📦 Мои заказы")]
    ],
    resize_keyboard=True
)

# Машина состояний для заказа
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    confirming = State()

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Добро пожаловать в Flower Delivery Bot!\nВыберите действие:", reply_markup=menu)

# Получение списка товаров через API
@dp.message(F.text == "🛍 Каталог")
async def catalog(message: types.Message):
    response = requests.get("http://127.0.0.1:8000/api/products/", headers=headers)

    if response.status_code == 200:
        products = response.json()
        if not products:
            await message.answer("❌ Каталог пуст!")
        else:
            for product in products:
                text = f"🌸 *{product['name']}*\n💰 Цена: {product['price']} ₽"
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🛍 Заказать", callback_data=f"order_{product['id']}")]
                    ]
                )
                await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer("❌ Ошибка загрузки каталога!")

# Обработчик нажатия кнопки "Заказать"
@dp.callback_query(lambda c: c.data.startswith("order_"))
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await callback.message.answer("📛 Введите ваше имя:")
    await state.set_state(OrderState.waiting_for_name)
    await callback.answer()

@dp.message(OrderState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    # Проверяем, что имя содержит только буквы и его длина корректна
    if not name.isalpha() or len(name) < 2 or len(name) > 50:
        await message.answer("❌ Имя должно содержать только буквы и быть длиной от 2 до 50 символов.\nВведите имя заново:")
        return

    await state.update_data(name=name)
    await message.answer("📞 Введите ваш номер телефона (только цифры):")
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "")  # Удаляем пробелы

    # Проверяем, что номер состоит только из цифр и имеет допустимую длину
    if not phone.isdigit():
        await message.answer("❌ Телефон должен содержать только цифры. Введите телефон заново:")
        return

    if not (5 <= len(phone) <= 15):
        await message.answer("❌ Телефон должен быть длиной от 5 до 15 символов. Введите телефон заново:")
        return

    await state.update_data(phone=phone)
    await message.answer("🏠 Введите ваш адрес (минимум 5 символов):")
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    address = message.text.strip()

    # Проверяем, что адрес не пустой и содержит минимум 5 символов
    if len(address) < 5:
        await message.answer("❌ Адрес должен содержать минимум 5 символов.\nВведите адрес заново:")
        return

    await state.update_data(address=address)

    data = await state.get_data()
    product_id = data["product_id"]
    name = data["name"]
    phone = data["phone"]
    address = data["address"]

    confirmation_text = (
        f"📦 Подтверждение заказа:\n"
        f"🛒 Товар ID: {product_id}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"🏠 Адрес: {address}\n\n"
        f"✅ Подтвердите заказ."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ]
    )

    await message.answer(confirmation_text, reply_markup=keyboard)
    await state.set_state(OrderState.confirming)

# Подтверждение заказа и уведомление админу
@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user_response = requests.get(
        f"http://127.0.0.1:8000/api/get_user/?telegram_id={callback.from_user.id}",
        headers=headers
    )

    if user_response.status_code != 200:
        await callback.message.answer("❌ Ошибка получения данных о пользователе!")
        await state.clear()
        return

    user_data = user_response.json()
    django_user_id = user_data["id"]

    order_data = {
        "user": django_user_id,
        "products": [data["product_id"]],
        "status": "new",
        "name": data["name"],
        "phone": data["phone"],
        "address": data["address"]
    }

    response = requests.post("http://127.0.0.1:8000/api/orders/", json=order_data, headers=headers)

    if response.status_code == 201:
        order_info = response.json()
        order_id = order_info["id"]

        admin_message = (
            f"📢 Новый заказ!\n"
            f"🆔 Заказ №{order_id}\n"
            f"👤 Пользователь ID: {django_user_id}\n"
            f"📦 Товар ID: {data['product_id']}\n"
            f"📛 Имя: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"🏠 Адрес: {data['address']}"
        )

        try:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_message)
            logging.info(f"✅ Уведомление админу {ADMIN_ID} отправлено.")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления админу: {e}")

        await callback.message.answer(f"✅ Ваш заказ №{order_id} успешно оформлен! 🎉")
    else:
        await callback.message.answer("❌ Ошибка оформления заказа!")

    await state.clear()
    await callback.answer()

@dp.message(F.text == "📦 Мои заказы")
async def my_orders(message: types.Message):
    user_telegram_id = message.from_user.id

    # Запрашиваем Django ID пользователя
    user_response = requests.get(
        f"http://127.0.0.1:8000/api/get_user/?telegram_id={user_telegram_id}",
        headers={"Authorization": f"Token {API_TOKEN}"}  # Добавляем API-токен
    )

    if user_response.status_code != 200:
        await message.answer("❌ Ошибка получения данных о пользователе!")
        return

    user_data = user_response.json()
    django_user_id = user_data["id"]

    # Запрашиваем заказы пользователя
    response = requests.get(
        f"http://127.0.0.1:8000/api/orders/?user={django_user_id}",
        headers={"Authorization": f"Token {API_TOKEN}"}  # Добавляем API-токен
    )

    if response.status_code == 200:
        orders = response.json()
        if not orders:
            await message.answer("❌ У вас пока нет заказов.")
        else:
            text = "📦 *Ваши заказы:*\n\n"
            for order in orders:
                product_id = order["products"][0]
                product_response = requests.get(
                    f"http://127.0.0.1:8000/api/products/{product_id}/",
                    headers={"Authorization": f"Token {API_TOKEN}"}  # Добавляем токен
                )

                if product_response.status_code == 200:
                    product_name = product_response.json().get("name", f"Товар ID {product_id}")
                else:
                    product_name = f"Товар ID {product_id}"

                # **Статус берем из API**
                status_mapping = {
                    "new": "🟡 Новый",
                    "processing": "🟠 В обработке",
                    "completed": "🟢 Завершён"
                }
                status = status_mapping.get(order["status"], "❓ Неизвестный статус")

                text += (
                    f"🛒 *Товар:* {product_name}\n"
                    f"📆 *Дата:* {order.get('created_at', 'Неизвестно')[:10]}\n"
                    f"🔘 *Статус:* {status}\n"
                    f"----------------------\n"
                )

            await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Ошибка загрузки заказов! Сервер вернул ошибку 401.")



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

def start_bot():
    asyncio.run(main())