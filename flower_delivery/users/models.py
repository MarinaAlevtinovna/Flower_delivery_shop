from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db import models

class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.username
