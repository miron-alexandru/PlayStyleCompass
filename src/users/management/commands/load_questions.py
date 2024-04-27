import csv
from django.core.management.base import BaseCommand
from users.models import QuizQuestion

class Command(BaseCommand):
    help = 'Loads quiz questions from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing quiz questions.')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            for idx, row in enumerate(reader, start=1):
                try:
                    name = row['name']
                except KeyError:
                    self.stdout.write(self.style.ERROR(f'Error in row {idx}: "name" field is missing'))
                    continue
                
                if QuizQuestion.objects.filter(name=name).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping question "{name}" as it already exists'))
                    continue
                
                question = QuizQuestion.objects.create(
                    name=name,
                    question_text=row['question_text'],
                    option1=row['option1'],
                    option2=row['option2'],
                    option3=row['option3'],
                    option4=row['option4']
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created question: {question.name}'))

