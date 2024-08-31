from django.core.management.base import BaseCommand
from playstyle_compass.models import Game
from googletrans import Translator

class Command(BaseCommand):
    help = 'Translate existing game descriptions and overviews to Romanian and save them.'

    def handle(self, *args, **kwargs):
        translator = Translator()

        games = Game.objects.all()
        for game in games:
            # Check if translations are already present
            if game.translated_description_ro and game.translated_overview_ro:
                self.stdout.write(self.style.SUCCESS(f'Skipped game: {game.title} (Already translated)'))
                continue

            # Translate description if available
            if game.description:
                translated_description = translate_text(game.description, 'ro', translator)
                game.translated_description_ro = translated_description

            # Translate overview if available
            if game.overview:
                translated_overview = translate_text(game.overview, 'ro', translator)
                game.translated_overview_ro = translated_overview

            # Save the updated game instance
            game.save()
            self.stdout.write(self.style.SUCCESS(f'Translated and saved game: {game.title}'))

        self.stdout.write(self.style.SUCCESS('Translation process completed for all games.'))

def translate_text(text, lang_code, translator):
    """
    Translates the given text to the specified language code using the provided translator.
    """
    try:
        translated_text = translator.translate(text, dest=lang_code).text
        return translated_text
    except Exception as e:
        print(f"Error translating text: {e}")
        return None
