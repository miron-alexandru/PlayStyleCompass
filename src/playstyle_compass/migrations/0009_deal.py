# Generated by Django 5.1.2 on 2025-03-10 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("playstyle_compass", "0008_poll_is_public"),
    ]

    operations = [
        migrations.CreateModel(
            name="Deal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("deal_id", models.CharField(max_length=255, unique=True)),
                ("game_name", models.CharField(max_length=255)),
                ("sale_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("retail_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("thumb_url", models.URLField()),
                ("store_name", models.CharField(max_length=255)),
                ("store_icon_url", models.URLField()),
            ],
        ),
    ]
