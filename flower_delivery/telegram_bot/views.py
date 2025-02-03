from django.http import HttpResponse
from .bot import start_bot
import threading

def run_bot(request):
    thread = threading.Thread(target=start_bot)
    thread.start()
    return HttpResponse("Бот запущен!")
