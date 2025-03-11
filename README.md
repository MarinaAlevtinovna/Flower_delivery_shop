# 🌸 Flower Delivery Shop

Flower Delivery Shop — это веб-приложение на Django, позволяющее пользователям заказывать цветы онлайн. 
Поддерживает корзину покупок, процесс оформления заказа и **уведомления в Telegram** через **Celery + Redis**.

---

## 📌 Установка проекта
1. **Клонируем репозиторий:**
    ```bash
    git clone https://github.com/yourusername/flower-delivery-shop.git
    ```
2. **Переходим в директорию проекта:**
    ```bash
    cd flower-delivery-shop
    ```
3. **Создаем виртуальное окружение:**
    ```bash
    python -m venv venv
    ```
4. **Активируем виртуальное окружение:**
    - Для Windows:
        ```bash
        .env\Scriptsctivate
        ```
    - Для MacOS/Linux:
        ```bash
        source venv/bin/activate
        ```
5. **Устанавливаем зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
6. **Запускаем миграции:**
    ```bash
    python manage.py migrate
    ```
7. **Запускаем сервер Django:**
    ```bash
    python manage.py runserver
    ```
После этого сайт будет доступен на [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 🔹 Запуск Redis
Redis используется как брокер задач для Celery.  
Если у тебя Windows:
1. **Перейди в папку Redis**  
   ```bash
   cd C:\Users\myssy\Redis
   ```
2. **Запусти сервер**:
   ```bash
   .\redis-server.exe
   ```

Если ты используешь **Linux/Mac**, просто запусти:
```bash
redis-server
```

---

## ⚙️ Запуск Celery
Celery нужен для обработки фоновых задач и отправки уведомлений.

1. **Запусти Redis (если еще не запущен).**
2. **Открой новый терминал, активируй виртуальное окружение:**
    ```bash
    .env\Scriptsctivate
    ```
3. **Запусти Celery (без `prefork`, чтобы избежать ошибок на Windows):**
    ```bash
    celery -A flower_delivery worker --loglevel=info --pool=solo
    ```

---

## 📩 Уведомления в Telegram
При изменении статуса заказа пользователю **автоматически отправляется уведомление** в Telegram.

- **Бот использует `aiogram`**, и его сессия теперь корректно закрывается.
- **Если уведомления не работают**, проверь:
  - **Celery запущен?**
  - **Redis работает? (`redis-cli PING` → `PONG`)**
  - **Бот настроен и имеет правильный токен?**

---

## 🛠 Возможные ошибки и их решения
### ❌ `Unclosed client session`
**Решение:** В `send_message()` убедись, что после отправки бот закрывает соединение:
```python
finally:
    await bot.session.close()
```

### ❌ `PermissionError(13, 'Отказано в доступе')` при завершении Celery
**Решение:** Принудительно заверши процессы Celery:
```bash
taskkill /F /IM celery.exe
```

### ❌ `No module named 'django'`
**Решение:** Убедись, что активировано виртуальное окружение и установлен Django:
```bash
.env\Scriptsctivate
pip install django
```

---

## ✨ Поддержка и развитие
Если у тебя есть идеи по улучшению, создавай Pull Request или Issue в репозитории. 😊
