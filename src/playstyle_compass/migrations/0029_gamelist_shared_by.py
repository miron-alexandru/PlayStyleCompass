# Generated by Django 5.1.2 on 2024-10-24 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0028_rename_shared_users_gamelist_shared_with"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamelist",
            name="shared_by",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
