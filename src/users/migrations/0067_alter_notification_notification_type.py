# Generated by Django 5.1.2 on 2024-10-17 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0066_alter_notification_message"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("review", "Review"),
                    ("follow", "Follow"),
                    ("friend_request", "Friend Request"),
                    ("message", "Message"),
                    ("chat_message", "Chat Message"),
                    ("shared_game", "Shared Game"),
                ],
                max_length=20,
            ),
        ),
    ]