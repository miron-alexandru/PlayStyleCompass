# Generated by Django 5.0.2 on 2024-04-21 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0026_quizquestion_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="quiz_taken_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
