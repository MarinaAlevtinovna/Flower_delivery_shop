import logging
import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from telegram_bot.bot import send_message
from asgiref.sync import sync_to_async
import nest_asyncio

# Применяем nest_asyncio для работы с асинхронными функциями в синхронном контексте
nest_asyncio.apply()

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a",
)

logger = logging.getLogger(__name__)

# Асинхронная обертка для отправки сообщения
async def send_message_async(chat_id, message):
    """Отправляет сообщение пользователю в боте"""
    logging.info(f"📤 Отправляем сообщение пользователю {chat_id}: {message}")
    try:
        await send_message(chat_id, message)
        logging.info(f"✅ Сообщение отправлено пользователю {chat_id}")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки сообщения {chat_id}: {e}")

# Функция для отправки уведомлений, которую нужно вызывать асинхронно
def send_order_status_update(instance):
    """Отправляет уведомление пользователю о смене статуса заказа"""
    logging.info(f"🚀 Запуск уведомления о смене статуса заказа {instance.id}")

    if not instance.user:
        logging.error(f"❌ Не удалось найти пользователя для заказа #{instance.id}")
        return

    if not instance.user.telegram_id:
        logging.warning(f"⚠️ У пользователя {instance.user.id} нет Telegram ID, уведомление не отправлено")
        return

    message = f"📦 Ваш заказ #{instance.id} теперь в статусе: {instance.status}"
    logging.info(f"📥 Генерация уведомления для пользователя {instance.user.telegram_id}: {message}")

    # Отправляем сообщение в бота синхронно
    send_message(instance.user.telegram_id, message)

# Обработчик сигнала изменения статуса заказа
@receiver(post_save, sender=Order)
def order_status_change_signal(sender, instance, **kwargs):
    """Синхронная функция для уведомления при изменении статуса заказа"""
    logger.info(f"🚀 Статус заказа #{instance.id} изменен на {instance.status}")

    if instance.user and instance.user.telegram_id:
        message = f"📦 Ваш заказ #{instance.id} теперь в статусе: {instance.status}"
        try:
            # Используем get_event_loop для выполнения асинхронной задачи
            loop = asyncio.get_event_loop()
            loop.create_task(send_message_async(instance.user.telegram_id, message))
            logger.info(f"✅ Сообщение отправлено пользователю {instance.user.telegram_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке сообщения: {e}")
    else:
        logger.warning(f"⚠️ У пользователя {instance.user} нет Telegram ID.")
