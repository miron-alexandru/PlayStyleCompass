# Generated by Django 5.1.2 on 2024-10-17 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0064_userprofile_receive_chat_message_notifications_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="delivered",
            field=models.BooleanField(default=False),
        ),
    ]