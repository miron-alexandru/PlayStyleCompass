# Generated by Django 5.0.2 on 2024-04-26 12:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0030_quizquestions_alter_quizuserresponse_question_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuizQuestion",
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
                ("name", models.CharField(max_length=100)),
                ("question_text", models.CharField(max_length=200)),
                ("option1", models.CharField(default="", max_length=150)),
                ("option2", models.CharField(default="", max_length=150)),
                ("option3", models.CharField(default="", max_length=150)),
                ("option4", models.CharField(default="", max_length=150)),
            ],
        ),
        migrations.AlterField(
            model_name="quizuserresponse",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="users.quizquestion"
            ),
        ),
        migrations.DeleteModel(
            name="QuizQuestions",
        ),
    ]
