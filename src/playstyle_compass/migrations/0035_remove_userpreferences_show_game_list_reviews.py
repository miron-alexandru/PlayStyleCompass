# Generated by Django 5.1.2 on 2024-11-10 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "playstyle_compass",
            "0034_rename_show_game_lists_userpreferences_show_game_list_reviews",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userpreferences",
            name="show_game_list_reviews",
        ),
    ]
