# Generated by Django 5.0.2 on 2024-08-01 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0050_chatmessage_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="is_online",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="last_online",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]