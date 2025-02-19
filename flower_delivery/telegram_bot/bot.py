import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .bot_config import BOT_TOKEN, API_TOKEN, ADMIN_ID
import logging
import os
from flower_delivery.settings import MEDIA_ROOT, SITE_URL, MEDIA_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a",
)

console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="📦 Мои заказы")]
    ],
    resize_keyboard=True
)

class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    confirming = State()

async def send_message(chat_id: int, message: str):
    try:
        await bot.send_message(chat_id, message)
        logging.info(f"📩 Уведомление отправлено пользователю {chat_id}: {message}")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки уведомления пользователю {chat_id}: {e}")


@dp.message(CommandStart())
async def start(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or f"user_{telegram_id}"

    try:
        user_response = requests.get(
            f"http://127.0.0.1:8000/api/get_user/?telegram_id={telegram_id}",
            headers=headers
        )

        print(f"👤 Ответ от сервера: {user_response.status_code}, {user_response.text}")

        if user_response.status_code == 200:
            user_data = user_response.json()

            if not user_data.get("telegram_id"):
                update_data = {"telegram_id": telegram_id}
                update_response = requests.patch(
                    f"http://127.0.0.1:8000/api/users/{user_data['id']}/",
                    json=update_data,
                    headers=headers
                )
                print(f"✅ Обновлен Telegram ID: {update_response.status_code}, {update_response.text}")

        else:
            create_user_data = {"username": username, "telegram_id": telegram_id}
            create_response = requests.post(
                "http://127.0.0.1:8000/api/users/",
                json=create_user_data,
                headers=headers
            )
            print(f"✅ Создан новый пользователь: {create_response.status_code}, {create_response.text}")

        await message.answer("✅ Вы зарегистрированы! Теперь вы будете получать уведомления о заказах.", reply_markup=menu)

    except Exception as e:
        print(f"❌ Ошибка при регистрации: {e}")
        await message.answer("⚠ Произошла ошибка при регистрации. Попробуйте ещё раз.")


@dp.message(F.text == "\U0001F6CD Каталог")
async def catalog(message: types.Message):
    response = requests.get(f"{SITE_URL}/api/catalog/", headers=headers)

    if response.status_code == 200:
        products = response.json()

        for product in products:
            image_path = product.get("image", "").strip()
            button = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛍 Заказать", callback_data=f"order_{product['id']}")]
            ])

            if image_path:
                if image_path.startswith(MEDIA_URL):
                    image_path = image_path[len(MEDIA_URL):]

                full_path = os.path.normpath(os.path.join(MEDIA_ROOT, image_path.lstrip("/")))

                logging.info(f"🔍 Проверяем путь: {full_path}")

                if os.path.exists(full_path):
                    try:
                        photo = FSInputFile(full_path)
                        logging.info(f"📸 Отправка фото: {full_path}")
                        await message.answer_photo(photo=photo, caption=f"{product['name']}\n💰 {product['price']} руб.", reply_markup=button)
                    except Exception as e:
                        logging.error(f"❌ Ошибка отправки фото: {e}")
                        await message.answer_photo(photo="https://via.placeholder.com/300", caption=f"{product['name']}\n💰 {product['price']} руб.", reply_markup=button)
                else:
                    logging.warning(f"⚠️ Файл не найден: {full_path}. Используем заглушку.")
                    await message.answer_photo(photo="https://via.placeholder.com/300", caption=f"{product['name']}\n💰 {product['price']} руб.", reply_markup=button)

    else:
        logging.error(f"❌ Ошибка загрузки каталога! Сервер вернул статус {response.status_code}.")
        await message.answer(f"❌ Ошибка загрузки каталога! Сервер вернул статус {response.status_code}.")

@dp.callback_query(lambda c: c.data.startswith("order_"))
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id, telegram_id=callback.from_user.id)
    await callback.message.answer("📛 Введите ваше имя:")
    await state.set_state(OrderState.waiting_for_name)
    await callback.answer()

@dp.message(OrderState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if not name.isalpha() or len(name) < 2 or len(name) > 50:
        await message.answer("❌ Имя должно содержать только буквы и быть длиной от 2 до 50 символов.\nВведите имя заново:")
        return

    await state.update_data(name=name)
    await message.answer("📞 Введите ваш номер телефона (только цифры):")
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "")

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
        "telegram_id": callback.from_user.id,
        "user": django_user_id,
        "products": [data["product_id"]],
        "status": "new",
        "name": data["name"],
        "phone": data["phone"],
        "address": data["address"]
    }

    print(f"📤 Отправляем заказ: {order_data}")
    response = requests.post("http://127.0.0.1:8000/api/orders/", json=order_data, headers=headers)
    print(f"📥 Ответ от сервера: {response.status_code}, {response.text}")

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
            f"🏠 Адрес: {data['address']}\n"
            f"🆔 Telegram ID: {callback.from_user.id}"
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

    user_response = requests.get(
        f"http://127.0.0.1:8000/api/get_user/?telegram_id={user_telegram_id}",
        headers={"Authorization": f"Token {API_TOKEN}"}
    )

    if user_response.status_code != 200:
        await message.answer("❌ Ошибка получения данных о пользователе!")
        return

    user_data = user_response.json()
    django_user_id = user_data["id"]

    response = requests.get(
        f"http://127.0.0.1:8000/api/orders/?telegram_id={user_telegram_id}",
        headers={"Authorization": f"Token {API_TOKEN}"}
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
                    headers={"Authorization": f"Token {API_TOKEN}"}
                )

                if product_response.status_code == 200:
                    product_name = product_response.json().get("name", f"Товар ID {product_id}")
                else:
                    product_name = f"Товар ID {product_id}"

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