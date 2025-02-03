from django.http import HttpResponse
import threading
from .bot import start_bot

def run_bot(request):
    thread = threading.Thread(target=start_bot, daemon=True)  # Даем боту работать в фоне
    thread.start()
    return HttpResponse("Бот запущен!")

