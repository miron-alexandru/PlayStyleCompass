# Generated by Django 5.1.2 on 2024-10-13 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "playstyle_compass",
            "0022_rename_connection_type_userpreferences_connection_types_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="is_casual",
            field=models.BooleanField(default=False),
        ),
    ]
