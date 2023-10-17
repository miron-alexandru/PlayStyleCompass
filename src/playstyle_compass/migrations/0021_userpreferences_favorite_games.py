# Generated by Django 4.2.4 on 2023-10-17 08:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("playstyle_compass", "0020_alter_game_release_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="userpreferences",
            name="favorite_games",
            field=models.ManyToManyField(
                blank=True, related_name="favorited_by", to="playstyle_compass.game"
            ),
        ),
    ]
