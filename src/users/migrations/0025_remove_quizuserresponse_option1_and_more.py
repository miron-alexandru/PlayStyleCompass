# Generated by Django 5.0.2 on 2024-04-17 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0024_quizuserresponse_option1_quizuserresponse_option2_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="quizuserresponse",
            name="option1",
        ),
        migrations.RemoveField(
            model_name="quizuserresponse",
            name="option2",
        ),
        migrations.RemoveField(
            model_name="quizuserresponse",
            name="option3",
        ),
        migrations.RemoveField(
            model_name="quizuserresponse",
            name="option4",
        ),
        migrations.AddField(
            model_name="quizquestion",
            name="option1",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="quizquestion",
            name="option2",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="quizquestion",
            name="option3",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="quizquestion",
            name="option4",
            field=models.CharField(default="", max_length=100),
        ),
    ]
