"""This module contains helper functions used in the users app."""

import random
from collections import defaultdict
from ..models import FriendList, QuizUserResponse, QuizQuestion
from playstyle_compass.models import Game
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ValidationError
from datetime import timedelta


def are_friends(user1, user2):
    """Function to check if two users are friends."""
    friend_list_user1, created = FriendList.objects.get_or_create(user=user1)
    friend_list_user2, created = FriendList.objects.get_or_create(user=user2)

    return friend_list_user1.is_friend(user2) and friend_list_user2.is_friend(user1)


def check_quiz_time(user):
    """Check if the user can take the quiz.
    Used to return the time str for quiz recommendations page info.
    """
    if last_update_time := user.userprofile.quiz_taken_date:
        one_day_ago = timezone.now() - timedelta(days=1)
        if last_update_time > one_day_ago:
            time_remaining = (last_update_time - one_day_ago).total_seconds()
            hours, remainder = divmod(time_remaining, 3600)
            minutes, _ = divmod(remainder, 60)

            if hours == 0 and minutes == 0:
                return None
            elif hours == 0:
                return f"{int(minutes)}m"
            elif minutes == 0:
                return f"{int(hours)}h"
            else:
                return f"{int(hours)}h:{int(minutes)}m"
    return None


class QuizRecommendations:
    """Class used to get game recommendations based on the Quiz responses."""

    def __init__(self, user_responses, user):
        self.user = user
        self.user_responses = user_responses

    def _calculate_concept_recommendations(self):
        """Calculate concept recommendations based on user responses."""
        concept_recommendations = defaultdict(int)

        for response in self.user_responses:
            concept = response.question.name
            response_text = response.response_text.lower()

            # Determine the number of games to recommend based on the response option
            if response_text == response.question.option1.lower():
                concept_recommendations[concept] += 4
            elif response_text == response.question.option2.lower():
                concept_recommendations[concept] += 2
            elif response_text == response.question.option3.lower():
                concept_recommendations[concept] += 1
            elif response_text == response.question.option4.lower():
                concept_recommendations[concept] -= 1

        return concept_recommendations

    def _get_games_for_concepts(self, concept_recommendations):
        """Retrieve games for recommended concepts."""
        recommended_game_guids = []
        recommended_games = []

        for concept, num_games in concept_recommendations.items():
            num_games = max(num_games, 1)
            # Query games for the concept that are not already recommended
            games = Game.objects.filter(concepts__icontains=concept).exclude(
                pk__in=recommended_game_guids
            )
            # Convert queryset to list for random selection
            games_list = list(games)
            # Randomly select recommended games
            selected_games = random.sample(games_list, min(num_games, len(games_list)))
            recommended_games.extend(selected_games)
            recommended_game_guids.extend([game.guid for game in selected_games])

        return recommended_games, recommended_game_guids

    def _save_recommendations_to_preferences(self, recommended_game_guids):
        """Save recommended game guids in user preferences."""
        self.user.userpreferences.quiz_recommendations = recommended_game_guids
        self.user.userpreferences.save()

    def get_recommendations(self):
        """Get game recommendations based on user responses."""
        concept_recommendations = self._calculate_concept_recommendations()
        recommended_games, recommended_game_guids = self._get_games_for_concepts(
            concept_recommendations
        )

        self._save_recommendations_to_preferences(recommended_game_guids)

        return recommended_games


def get_quiz_questions(user, cache_key):
    """Retrieve quiz questions either from cache or database."""
    if user.userprofile.quiz_taken:
        user.userprofile.quiz_taken = False
        user.userprofile.save()

    questions = list(QuizQuestion.objects.order_by("?")[:10])
    cache.set(cache_key, questions, timeout=None)
    return questions


def save_quiz_responses(user, questions, form):
    """Save user responses to the quiz."""
    for question in questions:
        option_selected = form.cleaned_data.get(f"question_{question.id}")

        if option_selected in ["option1", "option2", "option3", "option4"]:
            attribute_en = f"{option_selected}_en"
            attribute_ro = f"{option_selected}_ro"

            # Check if both translations exist and get the translated options
            if all(hasattr(question, attr) for attr in (attribute_en, attribute_ro)):
                option_en = getattr(question, attribute_en)
                option_ro = getattr(question, attribute_ro)

                QuizUserResponse.objects.update_or_create(
                    user=user,
                    question=question,
                    defaults={
                        "response_text_en": option_en,
                        "response_text_ro": option_ro,
                    },
                )
            else:
                raise ValidationError("Invalid option selected")
        else:
            raise ValidationError("Invalid option selected")
