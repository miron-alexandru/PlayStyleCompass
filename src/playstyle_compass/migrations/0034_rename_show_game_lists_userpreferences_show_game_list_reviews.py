# Generated by Django 5.1.2 on 2024-11-10 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0033_userpreferences_show_game_lists"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userpreferences",
            old_name="show_game_lists",
            new_name="show_game_list_reviews",
        ),
    ]
