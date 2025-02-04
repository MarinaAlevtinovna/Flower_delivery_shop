import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .bot_config import BOT_TOKEN, API_TOKEN, ADMIN_ID

# Настройки логирования
logging.basicConfig(level=logging.INFO)

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
    await state.update_data(name=message.text)
    await message.answer("📞 Введите ваш номер телефона:")
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏠 Введите ваш адрес:")
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)

    data = await state.get_data()
    confirmation_text = (
        f"📦 Подтверждение заказа:\n"
        f"🛒 Товар ID: {data['product_id']}\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🏠 Адрес: {data['address']}\n\n"
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
    user_response = requests.get(
        f"http://127.0.0.1:8000/api/get_user/?telegram_id={message.from_user.id}",
        headers=headers
    )

    if user_response.status_code != 200:
        await message.answer("❌ Ошибка получения данных о пользователе!")
        return

    user_data = user_response.json()
    django_user_id = user_data["id"]

    response = requests.get(f"http://127.0.0.1:8000/api/orders/?user={django_user_id}", headers=headers)

    if response.status_code == 200:
        orders = response.json()
        if not orders:
            await message.answer("❌ У вас пока нет заказов.")
        else:
            text = "\n".join([f"🛒 Заказ #{o['id']}: {o['status']}" for o in orders])
            await message.answer(f"📦 *Ваши заказы:*\n{text}", parse_mode="Markdown")
    else:
        await message.answer("❌ Ошибка загрузки заказов!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

def start_bot():
    asyncio.run(main())
