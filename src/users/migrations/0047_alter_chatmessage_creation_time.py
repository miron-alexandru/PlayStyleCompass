# Generated by Django 5.0.2 on 2024-07-16 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0046_chatmessage_creation_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="creation_time",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
