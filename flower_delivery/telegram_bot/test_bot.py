import unittest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, User, Chat
from orders.signals import send_order_status_update

class TestTelegramBot(unittest.IsolatedAsyncioTestCase):
    async def test_catalog_command(self):
        message = AsyncMock(spec=Message)
        message.message_id = 1
        message.chat = AsyncMock(spec=Chat, id=1234, type="private")
        message.text = "Каталог"
        message.answer = AsyncMock()

        with patch("telegram_bot.bot.catalog", new_callable=AsyncMock) as mock_catalog:
            await mock_catalog(message)
            mock_catalog.assert_called_once_with(message)

    async def test_send_order_status_update(self):
        user_id = "123456789"
        order_id = 42
        status = "completed"

        instance_mock = AsyncMock()
        instance_mock.id = order_id
        instance_mock.user = AsyncMock()
        instance_mock.user.username = user_id
        instance_mock.status = status

        with patch("orders.signals.send_message", new_callable=AsyncMock) as mock_send_message:
            await send_order_status_update(sender=None, instance=instance_mock)
            mock_send_message.assert_called_once_with(
                int(user_id),
                f"📦 Обновление заказа №{order_id}\n🔘 Новый статус: 🟢 Завершён\nСпасибо, что выбираете нас! 💐"
            )

if __name__ == "__main__":
    unittest.main()
