import logging
import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, CustomUser
from telegram_bot.bot import bot

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a",
)

def send_message(chat_id, message):
    try:
        asyncio.run(send_message_async(chat_id, message))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_message_async(chat_id, message))

async def send_message_async(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logging.info(f"✅ Уведомление пользователю {chat_id} отправлено.")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки уведомления пользователю {chat_id}: {e}")

@receiver(post_save, sender=Order)
def send_order_status_update(sender, instance, **kwargs):
    user = instance.user

    if user:
        if user.telegram_id is None:
            logging.warning(f"⚠️ У пользователя {user.username} отсутствует Telegram ID.")
        else:
            telegram_id = user.telegram_id
            message = f"📦 Статус вашего заказа #{instance.id} изменен на: {instance.status}"
            send_message(telegram_id, message)
    else:
        logging.error(f"❌ Ошибка: У заказа #{instance.id} нет привязанного пользователя.")
