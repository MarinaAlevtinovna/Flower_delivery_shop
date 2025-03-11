import logging
import asyncio
import multiprocessing
from django.db.models.signals import post_save
from django.dispatch import receiver
from telegram_bot.bot import send_message
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.apps import apps
Order = apps.get_model("orders", "Order")
User = get_user_model()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

def send_message_process(telegram_id, message):
    """Функция-обертка для отправки уведомления в отдельном процессе"""
    try:
        async_to_sync(send_message)(telegram_id, message)
        logger.info(f"✅ Уведомление успешно отправлено пользователю {telegram_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомления пользователю {telegram_id}: {e}")

def send_order_status_update(instance):
    """Отправляет уведомление пользователю о смене статуса заказа в отдельном процессе"""
    if not instance.user or not instance.user.telegram_id:
        logger.warning(f"⚠️ У пользователя {instance.user} нет Telegram ID, уведомление не отправлено")
        return

    message = f"📦 Ваш заказ #{instance.id} теперь в статусе: {instance.status}"
    logger.info(f"📥 Генерация уведомления для пользователя {instance.user.telegram_id}: {message}")

    # Запускаем отправку в отдельном процессе
    process = multiprocessing.Process(target=send_message_process, args=(instance.user.telegram_id, message))
    process.start()
    logger.info(f"✅ Уведомление отправляется в отдельном процессе пользователю {instance.user.telegram_id}")

@receiver(post_save, sender=Order)
def order_status_change_signal(sender, instance, **kwargs):
    """📢 Уведомляет пользователя о смене статуса заказа"""
    logger.info(f"🚀 Статус заказа #{instance.id} изменен на {instance.status}")

    try:
        send_order_status_update(instance)
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомления пользователю {instance.user.telegram_id}: {e}")
