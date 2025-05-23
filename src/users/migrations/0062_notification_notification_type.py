# Generated by Django 5.1.2 on 2024-10-17 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0061_follow"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("review", "Review"),
                    ("follow", "Follow"),
                    ("friend_request", "Friend Request"),
                    ("message", "Message"),
                    ("chat_message", "Chat Message"),
                ],
                default="",
                max_length=20,
            ),
            preserve_default=False,
        ),
    ]
