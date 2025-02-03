from django.urls import path
from .views import run_bot

urlpatterns = [
    path("start/", run_bot, name="start_bot"),
]
