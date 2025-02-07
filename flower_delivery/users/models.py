from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.username
