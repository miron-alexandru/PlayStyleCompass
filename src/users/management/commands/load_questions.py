"""Command used to load and create Quiz questions from a CSV file."""

import csv
from django.core.management.base import BaseCommand
from users.models import QuizQuestion


class Command(BaseCommand):
    help = "Loads quiz questions from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            nargs="?",  # Makes this argument optional
            default="src/users/quiz/quiz_questions.csv",
            help="Path to the CSV file containing quiz questions. Defaults to 'src/users/quiz/quiz_questions.csv'."
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        with open(csv_file, "r") as file:
            reader = csv.DictReader(file, delimiter=";")
            for idx, row in enumerate(reader, start=1):
                try:
                    name = row["name"]
                except KeyError:
                    self.stdout.write(
                        self.style.ERROR(f'Error in row {idx}: "name" field is missing')
                    )
                    continue

                if QuizQuestion.objects.filter(name=name).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping question "{name}" as it already exists'
                        )
                    )
                    continue

                question = QuizQuestion.objects.create(
                    name=name,
                    question_text_en=row["question_text_en"],
                    question_text_ro=row["question_text_ro"],
                    option1_en=row["option1_en"],
                    option1_ro=row["option1_ro"],
                    option2_en=row["option2_en"],
                    option2_ro=row["option2_ro"],
                    option3_en=row["option3_en"],
                    option3_ro=row["option3_ro"],
                    option4_en=row["option4_en"],
                    option4_ro=row["option4_ro"],
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created question: {question.name}"
                    )
                )
