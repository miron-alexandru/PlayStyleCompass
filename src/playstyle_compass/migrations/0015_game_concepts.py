# Generated by Django 5.0.2 on 2024-04-24 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0014_gamemodes"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="concepts",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
    ]