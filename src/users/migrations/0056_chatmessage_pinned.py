# Generated by Django 5.0.2 on 2024-08-16 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0055_chatmessage_file_size"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="pinned",
            field=models.BooleanField(default=False),
        ),
    ]
