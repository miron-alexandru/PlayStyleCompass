# Generated by Django 5.1.2 on 2024-10-20 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0024_gamelist"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="gamelist",
            name="games",
        ),
        migrations.AddField(
            model_name="gamelist",
            name="game_guids",
            field=models.JSONField(default=list),
        ),
    ]