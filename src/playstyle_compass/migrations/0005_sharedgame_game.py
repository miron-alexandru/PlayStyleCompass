# Generated by Django 4.2.4 on 2024-01-11 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("playstyle_compass", "0004_alter_sharedgame_receiver_alter_sharedgame_sender"),
    ]

    operations = [
        migrations.AddField(
            model_name="sharedgame",
            name="game",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="playstyle_compass.game",
            ),
            preserve_default=False,
        ),
    ]
