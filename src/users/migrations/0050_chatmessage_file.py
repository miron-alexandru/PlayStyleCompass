# Generated by Django 5.0.2 on 2024-07-28 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0049_chatmessage_edited"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="file",
            field=models.URLField(blank=True, null=True),
        ),
    ]