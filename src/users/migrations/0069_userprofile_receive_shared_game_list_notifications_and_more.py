# Generated by Django 5.1.2 on 2024-10-23 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0068_userprofile_receiver_shared_game_notifications_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="receive_shared_game_list_notifications",
            field=models.BooleanField(default=True),
        ),
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
                    ("shared_game_list", "Shared Game List"),
                ],
                max_length=20,
            ),
        ),
    ]