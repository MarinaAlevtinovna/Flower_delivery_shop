# Generated by Django 5.1.5 on 2025-02-05 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='telegram_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
    ]
