# Generated by Django 5.1.2 on 2024-10-22 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0026_gamelist_additional_games"),
    ]

    operations = [
        migrations.RenameField(
            model_name="gamelist",
            old_name="shared_with",
            new_name="shared_users",
        ),
    ]