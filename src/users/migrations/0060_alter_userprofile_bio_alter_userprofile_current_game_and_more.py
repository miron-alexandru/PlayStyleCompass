# Generated by Django 5.0.2 on 2024-09-25 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0059_alter_userprofile_gaming_commitment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="bio",
            field=models.TextField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="current_game",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="favorite_character",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="favorite_franchise",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="favorite_game",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="favorite_game_modes",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="favorite_soundtrack",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="gaming_alias",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="gaming_commitment",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="last_finished_game",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="main_gaming_platform",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="social_media",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="streaming_preferences",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]
