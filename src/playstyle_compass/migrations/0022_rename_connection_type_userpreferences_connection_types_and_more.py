# Generated by Django 5.0.2 on 2024-10-04 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0021_userpreferences_connection_type_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userpreferences",
            old_name="connection_type",
            new_name="connection_types",
        ),
        migrations.RenameField(
            model_name="userpreferences",
            old_name="game_style",
            new_name="game_styles",
        ),
    ]
