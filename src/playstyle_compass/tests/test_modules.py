import os
import sys
from decimal import Decimal

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db.models import Avg
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import now, timedelta
from playstyle_compass.models import *

User = get_user_model()


class GameModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            guid="game-123",
            title="Test Game",
            description="A test game description",
            overview="A short overview",
            genres="Action",
            platforms="PC",
            themes="Adventure",
            image="http://example.com/image.jpg",
            release_date="2025-01-01",
            developers="Test Devs",
            game_images="http://example.com/image1.jpg,http://example.com/image2.jpg",
            similar_games="Another Game",
            dlcs="DLC1,DLC2",
            franchises="Franchise X",
            videos="http://example.com/video.mp4",
            concepts="Open World",
            is_casual=True,
            is_popular=True,
            playtime="10 hours",
            pc_req_min="Intel i5, 8GB RAM",
            pc_req_rec="Intel i7, 16GB RAM",
            mac_req_min="M1, 8GB RAM",
            mac_req_rec="M2, 16GB RAM",
            linux_req_min="AMD Ryzen 5",
            linux_req_rec="Ryzen 7, 16GB",
            average_score=None,
            total_reviews=None,
            translated_description_ro="Descriere test",
            translated_overview_ro="Prezentare generală test",
        )

    def test_str_representation(self):
        """Test the string representation of the Game model."""
        self.assertEqual(str(self.game), "Test Game")

    def test_game_creation_fields(self):
        """Test that the Game object is created with correct field values."""
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(self.game.guid, "game-123")
        self.assertEqual(self.game.title, "Test Game")
        self.assertTrue(self.game.is_casual)
        self.assertTrue(self.game.is_popular)
        self.assertEqual(self.game.playtime, "10 hours")
        self.assertIn(self.game.average_score, (None, 0))
        self.assertEqual(self.game.total_reviews, 0)

    def test_update_score_no_reviews(self):
        """Test score update when no reviews exist."""
        self.game.update_score()
        self.assertEqual(self.game.total_reviews, 0)
        self.assertEqual(self.game.average_score, 0)

    def test_update_score_with_reviews(self):
        """Test score update with existing reviews."""
        Review.objects.create(game=self.game, score=4)
        Review.objects.create(game=self.game, score=2)
        self.game.update_score()
        self.assertEqual(self.game.total_reviews, 2)
        self.assertEqual(self.game.average_score, 3.0)

    def test_stores_property(self):
        """Test stores property returns correct related stores."""
        GameStores.objects.create(
            guid="game-123", store_name="Steam", title="The Witcher"
        )
        GameStores.objects.create(guid="game-123", store_name="Epic", title="FIFA")
        stores = self.game.stores
        self.assertEqual(stores.count(), 2)
        store_names = [store.store_name for store in stores]
        self.assertIn("Steam", store_names)
        self.assertIn("Epic", store_names)


class GameStoresModelTest(TestCase):
    def setUp(self):
        self.store = GameStores.objects.create(
            guid="game-123",
            title="Test Game",
            store_name="Steam",
            store_url="https://store.steampowered.com/app/123",
        )

    def test_str_representation(self):
        expected_str = "Steam (Test Game)"
        self.assertEqual(str(self.store), expected_str)

    def test_creation(self):
        self.assertEqual(GameStores.objects.count(), 1)
        self.assertEqual(self.store.guid, "game-123")
        self.assertEqual(self.store.store_name, "Steam")
        self.assertEqual(self.store.store_url, "https://store.steampowered.com/app/123")


class UserPreferencesModelTest(TestCase):
    def setUp(self):
        # Create a user and two games
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.game1 = Game.objects.create(
            guid="game-1",
            title="Game One",
            description="Desc 1",
            genres="Action",
            platforms="PC",
            themes="Theme1",
            image="http://example.com/image1.jpg",
            videos="",
            concepts="Concept1",
        )
        self.game2 = Game.objects.create(
            guid="game-2",
            title="Game Two",
            description="Desc 2",
            genres="Adventure",
            platforms="PC",
            themes="Theme2",
            image="http://example.com/image2.jpg",
            videos="",
            concepts="Concept2",
        )
        # Create UserPreferences for the user (or get existing)
        self.preferences, created = UserPreferences.objects.get_or_create(
            user=self.user
        )

    def test_str_representation(self):
        expected_str = f"{self.user}'s user preferences"
        self.assertEqual(str(self.preferences), expected_str)

    def test_add_and_remove_favorite_games(self):
        # Initially no favorite games
        self.assertEqual(self.preferences.get_favorite_games().count(), 0)

        # Add game1 and check it's there
        self.preferences.add_favorite_game(self.game1)
        self.assertIn(self.game1, self.preferences.get_favorite_games())

        # Add game2 and check both are there
        self.preferences.add_favorite_game(self.game2)
        self.assertIn(self.game2, self.preferences.get_favorite_games())

        # Remove game1 and check it is removed
        self.preferences.remove_favorite_game(self.game1)
        self.assertNotIn(self.game1, self.preferences.get_favorite_games())

    def test_add_and_remove_game_queue(self):
        # Initially no games in queue
        self.assertEqual(self.preferences.get_game_queue().count(), 0)

        # Add game1 to queue and check
        self.preferences.add_game_to_queue(self.game1)
        self.assertIn(self.game1, self.preferences.get_game_queue())

        # Add game2 to queue and check both are there
        self.preferences.add_game_to_queue(self.game2)
        self.assertIn(self.game2, self.preferences.get_game_queue())

        # Remove game1 from queue and check it is removed
        self.preferences.remove_game_from_queue(self.game1)
        self.assertNotIn(self.game1, self.preferences.get_game_queue())


class SharedGameTestModel(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="testuser1", password="testpass1"
        )
        self.receiver = User.objects.create_user(
            username="testuser2", password="testpass2"
        )

        self.shared_game = SharedGame.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Testing content",
            game_id=1234,
        )

    def test_str_representation(self):
        """Test the string representation of the Shared Game model."""
        expected_str = f"SharedGame from {self.sender} to {self.receiver}"
        self.assertEqual(str(self.shared_game), expected_str)

    def test_shared_game_creation(self):
        """Test the creation of the Shared Game model."""
        self.assertEqual(self.shared_game.sender, self.sender)
        self.assertEqual(self.shared_game.receiver, self.receiver)
        self.assertEqual(self.shared_game.content, "Testing content")
        self.assertEqual(self.shared_game.game_id, 1234)
        self.assertFalse(self.shared_game.is_deleted_by_sender)
        self.assertFalse(self.shared_game.is_deleted_by_receiver)
        self.assertIsNotNone(self.shared_game.timestamp)


class ReviewModelTest(TestCase):
    def setUp(self):
        # Create a game, a user and a review
        self.game = Game.objects.create(
            guid="game-1",
            title="Test Game",
            description="A test game",
            genres="Action",
            platforms="PC",
            themes="Theme1",
            image="http://example.com/image.jpg",
            videos="",
            concepts="Concept1",
        )
        self.user = User.objects.create_user(username="reviewer", password="pass123")
        self.review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="Reviewer1",
            review_deck="Short deck",
            review_description="This is a detailed review description.",
            score=4,
            likes=0,
            dislikes=0,
            liked_by="",
            disliked_by="",
            date_added=now(),
        )

    def test_review_creation_and_str(self):
        self.assertEqual(self.review.reviewers, "Reviewer1")
        self.assertEqual(self.review.score, 4)
        self.assertEqual(str(self.review), f"Review by Reviewer1 for {self.game.title}")

    def test_like_unlike_review(self):
        user_id = self.user.id

        # Initially no likes
        self.assertEqual(self.review.likes, 0)
        self.assertFalse(self.review.user_has_liked(user_id))

        # Add a like
        self.review.add_like(user_id)
        self.review.refresh_from_db()
        self.assertEqual(self.review.likes, 1)
        self.assertTrue(self.review.user_has_liked(user_id))
        self.assertIn(str(user_id), self.review.liked_by)

        # Add like again should not increment
        self.review.add_like(user_id)
        self.review.refresh_from_db()
        self.assertEqual(self.review.likes, 1)  # no double count

        # Remove like
        self.review.remove_like(user_id)
        self.review.refresh_from_db()
        self.assertEqual(self.review.likes, 0)
        self.assertFalse(self.review.user_has_liked(user_id))

    def test_dislike_undislike_review(self):
        user_id = self.user.id

        # Initially no dislikes
        self.assertEqual(self.review.dislikes, 0)
        self.assertFalse(self.review.user_has_disliked(user_id))

        # Add a dislike
        self.review.add_dislike(user_id)
        self.review.refresh_from_db()
        self.assertEqual(self.review.dislikes, 1)
        self.assertTrue(self.review.user_has_disliked(user_id))
        self.assertIn(str(user_id), self.review.disliked_by)

        # Add dislike again should not increment
        self.review.add_dislike(user_id)
        self.review.refresh_from_db()
        self.assertEqual(self.review.dislikes, 1)  # no double count

        # Remove dislike
        self.review.remove_dislike(user_id)
        self.review.refresh_from_db()
        self.assertEqual(self.review.dislikes, 0)
        self.assertFalse(self.review.user_has_disliked(user_id))

    def test_save_updates_game_score(self):
        # Mock the game's update_score method to track calls
        called = []

        def mock_update_score():
            called.append(True)

        self.game.update_score = mock_update_score

        # Save review triggers game.update_score
        self.review.save()
        self.assertTrue(called)

    def test_delete_updates_game_score(self):
        # Mock the game's update_score method to track calls
        called = []

        def mock_update_score():
            called.append(True)

        self.game.update_score = mock_update_score

        # Delete review triggers game.update_score
        self.review.delete()
        self.assertTrue(called)


class FranchiseModelTest(TestCase):
    def setUp(self):
        self.franchise = Franchise.objects.create(
            title="Legend Series",
            description="Epic adventure games",
            overview="All games in the Legend franchise",
            games="1,2,3",
            image="http://example.com/legend.jpg",
            images="http://example.com/legend1.jpg,http://example.com/legend2.jpg",
        )

    def test_str_representation(self):
        self.assertEqual(str(self.franchise), "Franchise: Legend Series")

    def test_update_games_count(self):
        self.franchise.update_games_count()
        self.assertEqual(self.franchise.games_count, 3)


class CharacterModelTest(TestCase):
    def setUp(self):
        self.character = Character.objects.create(
            name="Arthas",
            deck="A brave warrior",
            description="Once a noble prince",
            birthday="1995-06-01",
            friends="Jaina",
            enemies="Illidan",
            games="Warcraft III, WoW",
            first_game="Warcraft III",
            franchises="Warcraft",
            image="http://example.com/arthas.jpg",
            images="http://example.com/arthas1.jpg,http://example.com/arthas2.jpg",
            character_id=101,
        )

    def test_str_representation(self):
        self.assertEqual(str(self.character), "Character: Arthas")

    def test_fields_saved_correctly(self):
        self.assertEqual(self.character.name, "Arthas")
        self.assertIn("WoW", self.character.games)
        self.assertEqual(self.character.first_game, "Warcraft III")


class GameModesModelTest(TestCase):
    def setUp(self):
        self.game_mode = GameModes.objects.create(
            game_id="gm123", game_name="BattleZone", game_mode="Multiplayer"
        )

    def test_str_representation(self):
        self.assertEqual(str(self.game_mode), "BattleZone - Multiplayer")

    def test_fields(self):
        self.assertEqual(self.game_mode.game_id, "gm123")
        self.assertEqual(self.game_mode.game_mode, "Multiplayer")


class NewsModelTest(TestCase):
    def setUp(self):
        self.news = News.objects.create(
            article_id="ART123",
            title="New RPG Game Announced",
            summary="A new RPG title has been revealed for next-gen consoles.",
            url="https://example.com/news/rpg-game",
            image="https://example.com/images/rpg.jpg",
            publish_date="2025-06-01",
            platforms="PC, PS5",
        )

    def test_str_representation(self):
        self.assertEqual(str(self.news), "Article: New RPG Game Announced")

    def test_fields_are_stored_correctly(self):
        self.assertEqual(self.news.article_id, "ART123")
        self.assertEqual(self.news.title, "New RPG Game Announced")
        self.assertEqual(
            self.news.summary,
            "A new RPG title has been revealed for next-gen consoles.",
        )
        self.assertEqual(self.news.url, "https://example.com/news/rpg-game")
        self.assertEqual(self.news.image, "https://example.com/images/rpg.jpg")
        self.assertEqual(self.news.publish_date, "2025-06-01")
        self.assertEqual(self.news.platforms, "PC, PS5")

    def test_optional_fields_can_be_blank(self):
        news_blank = News.objects.create(title="Indie Showcase Event Announced")
        self.assertIsNone(news_blank.article_id)
        self.assertEqual(news_blank.title, "Indie Showcase Event Announced")
        self.assertIsNone(news_blank.summary)
        self.assertIsNone(news_blank.url)
        self.assertIsNone(news_blank.image)
        self.assertIsNone(news_blank.publish_date)
        self.assertIsNone(news_blank.platforms)


class GameListModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.user1 = User.objects.create_user(username="user1", password="testpass")
        self.user2 = User.objects.create_user(username="user2", password="testpass")

        self.game_list = GameList.objects.create(
            owner=self.owner,
            title="Top RPG Games",
            description="A list of great RPGs.",
            game_guids=["game-1", "game-2", "game-3"],
            additional_games="game-4,game-5",
            shared_by={"via": "link"},
        )

    def test_str_representation(self):
        expected = "Top RPG Games (Owner: owner, Games: 5)"
        self.assertEqual(str(self.game_list), expected)

    def test_total_games_property(self):
        self.assertEqual(self.game_list.total_games, 5)

    def test_like_and_like_count(self):
        self.game_list.liked_by.add(self.user1, self.user2)
        self.assertEqual(self.game_list.like_count, 2)

    def test_share_and_share_count(self):
        self.game_list.shared_with.add(self.user1)
        self.assertEqual(self.game_list.share_count, 1)

    def test_favorite_and_favorite_count(self):
        self.game_list.favorites.add(self.user1)
        self.assertEqual(self.game_list.favorite_count, 1)

    def test_toggle_favorite_add(self):
        result = self.game_list.toggle_favorite(self.user2)
        self.assertTrue(result)
        self.assertIn(self.user2, self.game_list.favorites.all())

    def test_toggle_favorite_remove(self):
        self.game_list.favorites.add(self.user1)
        result = self.game_list.toggle_favorite(self.user1)
        self.assertFalse(result)
        self.assertNotIn(self.user1, self.game_list.favorites.all())

    def test_updated_fields(self):
        self.game_list.title = "Updated List Title"
        self.game_list.save()
        self.assertEqual(self.game_list.title, "Updated List Title")


class ListReviewModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.reviewer = User.objects.create_user(
            username="reviewer", password="testpass"
        )
        self.user1 = User.objects.create_user(username="user1", password="testpass")

        self.game_list = GameList.objects.create(
            owner=self.owner, title="Top Action Games", game_guids=["game-1", "game-2"]
        )

        self.review = ListReview.objects.create(
            game_list=self.game_list,
            user=self.reviewer,
            title="Solid picks!",
            rating=4,
            review_text="Enjoyed every game on this list.",
        )

    def test_str_representation(self):
        expected = f"Review by {self.reviewer} on {self.game_list}"
        self.assertEqual(str(self.review), expected)

    def test_like_count_initial(self):
        self.assertEqual(self.review.like_count, 0)

    def test_add_like_and_count(self):
        self.review.liked_by.add(self.user1)
        self.assertEqual(self.review.like_count, 1)
        self.assertIn(self.user1, self.review.liked_by.all())

    def test_rating_boundaries_valid(self):
        self.review.rating = 5
        self.review.full_clean()

        self.review.rating = 1
        self.review.full_clean()

    def test_rating_out_of_bounds_invalid(self):
        self.review.rating = 0
        with self.assertRaises(ValidationError):
            self.review.full_clean()

        self.review.rating = 6
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_unique_review_per_user_and_game_list(self):
        with self.assertRaises(IntegrityError):
            ListReview.objects.create(
                game_list=self.game_list,
                user=self.reviewer,
                title="Another review",
                rating=3,
            )


class ListCommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.game_list = GameList.objects.create(
            owner=self.user, title="Top Action Games", game_guids=["game-1", "game-2"]
        )

        self.list_comment = ListComment.objects.create(
            game_list=self.game_list,
            user=self.user,
            text="Test Comment",
        )

    def test_comment_creation(self):
        self.assertEqual(self.list_comment.text, "Test Comment")
        self.assertEqual(self.list_comment.user, self.user)
        self.assertIsNotNone(self.list_comment.created_at)
        self.assertIsNotNone(self.list_comment.updated_at)

    def test_str_representation(self):
        expected = f"List Comment by {self.user} on {self.game_list}"
        self.assertEqual(str(self.list_comment), expected)

    def test_comment_like(self):
        self.list_comment.liked_by.add(self.user)
        self.assertEqual(self.list_comment.like_count, 1)
        self.assertIn(self.user, self.list_comment.liked_by.all())

    def test_like_count_default(self):
        self.assertEqual(self.list_comment.like_count, 0)

    def test_comments_ordering(self):
        ListComment.objects.create(
            game_list=self.game_list, user=self.user, text="Second"
        )
        ListComment.objects.create(
            game_list=self.game_list, user=self.user, text="Third"
        )
        comments = ListComment.objects.filter(game_list=self.game_list)
        dates = [comment.created_at for comment in comments]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_is_editable_within_10_minutes(self):
        comment = ListComment.objects.create(
            game_list=self.game_list,
            user=self.user,
            text="Test Comment",
        )
        self.assertTrue(comment.is_editable())

    def test_is_not_editable_after_10_minutes(self):
        comment = ListComment.objects.create(
            game_list=self.game_list,
            user=self.user,
            text="Test Comment",
        )
        # Simulate a creation time more than 10 minutes ago
        comment.created_at = now() - timedelta(minutes=11)
        comment.save(update_fields=["created_at"])
        self.assertFalse(comment.is_editable())


class PollModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass"
        )
        self.poll = Poll.objects.create(
            title="Test Title",
            description="Nice description",
            created_by=self.user,
        )

        self.option1 = PollOption.objects.create(poll=self.poll, text="Option 1")
        self.option2 = PollOption.objects.create(poll=self.poll, text="Option 2")

    def test_poll_creation(self):
        self.assertEqual(self.poll.title, "Test Title")
        self.assertEqual(self.poll.description, "Nice description")
        self.assertEqual(self.poll.created_by, self.user)
        self.assertIsNotNone(self.poll.created_at)
        self.assertEqual(self.poll.liked_by.count(), 0)
        self.assertEqual(self.poll.shared_with.count(), 0)
        self.assertEqual(self.poll.shared_by, {})
        self.assertEqual(self.poll.duration, timedelta(days=7))
        self.assertTrue(self.poll.is_public)

    def test_str_representation(self):
        expected_str = f"Poll: Test Title (Created by {self.user})"
        self.assertEqual(str(self.poll), expected_str)

    def test_end_time_property(self):
        expected_end = self.poll.created_at + self.poll.duration
        self.assertEqual(self.poll.end_time, expected_end)

    def test_has_ended_false(self):
        self.assertFalse(self.poll.has_ended())

    def test_has_ended_true(self):
        self.poll.created_at = now() - timedelta(days=8)
        self.poll.save(update_fields=["created_at"])
        self.assertTrue(self.poll.has_ended())

    def test_like_count_property(self):
        self.poll.liked_by.add(self.user)
        self.assertEqual(self.poll.like_count, 1)

    def test_total_votes_and_options_with_percentages(self):
        # Cast votes
        Vote.objects.create(user=self.user, poll=self.poll, option=self.option1)
        Vote.objects.create(user=self.other_user, poll=self.poll, option=self.option1)

        total_votes = self.poll.total_votes()
        self.assertEqual(total_votes, 2)

        options_with_percentages = self.poll.options_with_percentages()
        self.assertEqual(len(options_with_percentages), 2)

        option1_percentage = next(
            (
                opt["percentage"]
                for opt in options_with_percentages
                if opt["option"] == self.option1
            ),
            None,
        )
        self.assertEqual(option1_percentage, 100.0)

        option2_percentage = next(
            (
                opt["percentage"]
                for opt in options_with_percentages
                if opt["option"] == self.option2
            ),
            None,
        )
        self.assertEqual(option2_percentage, 0.0)

    def test_user_vote(self):
        vote = Vote.objects.create(user=self.user, poll=self.poll, option=self.option1)
        self.assertEqual(self.poll.user_vote(self.user), self.option1)

    def test_user_vote_none(self):
        self.assertIsNone(self.poll.user_vote(self.other_user))


class PollOptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.poll = Poll.objects.create(
            title="Test Title",
            description="Nice description",
            created_by=self.user,
        )

        self.option = PollOption.objects.create(poll=self.poll, text="Option 1")

    def test_creation_and_str(self):
        self.assertEqual(self.option.poll, self.poll)
        self.assertEqual(self.option.text, "Option 1")
        expected_str = f"Poll option 'Option 1' for the poll {self.poll}"
        self.assertEqual(str(self.option), expected_str)

    def test_multiple_options(self):
        opt2 = PollOption.objects.create(poll=self.poll, text="Option 2")
        self.assertEqual(self.poll.options.count(), 2)


class VoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.poll = Poll.objects.create(
            title="Test Title",
            description="Nice description",
            created_by=self.user,
        )

        self.option = PollOption.objects.create(poll=self.poll, text="Option 1")

        self.vote = Vote.objects.create(
            poll=self.poll, option=self.option, user=self.user
        )

    def test_str_representation(self):
        expected_str = (
            f"Vote: User {self.user} voted for 'Option 1' in poll 'Test Title'"
        )
        self.assertEqual(str(self.vote), expected_str)

    def test_vote_creation(self):
        self.assertEqual(self.vote.poll, self.poll)
        self.assertEqual(self.vote.option, self.option)
        self.assertEqual(self.vote.user, self.user)
        self.assertIsNotNone(self.vote.voted_at)

    def test_duplicate_vote_raises_error(self):
        with self.assertRaises(IntegrityError):
            Vote.objects.create(poll=self.poll, option=self.option, user=self.user)


class DealModelTest(TestCase):
    def setUp(self):
        self.deal = Deal.objects.create(
            deal_id="12345",
            game_name="Hades",
            sale_price=Decimal("14.99"),
            retail_price=Decimal("24.99"),
            thumb_url="http://example.com/thumb.jpg",
            store_name="Steam",
            store_icon_url="http://example.com/icon.jpg",
        )

    def test_deal_creation(self):
        self.assertEqual(self.deal.game_name, "Hades")
        self.assertEqual(self.deal.sale_price, Decimal("14.99"))

    def test_str_representation(self):
        self.assertEqual(str(self.deal), "Hades - $14.99")

    def test_store_url_property(self):
        self.assertIn(self.deal.store_url, ["https://store.steampowered.com/", "#"])


class SharedDealModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.recipient = User.objects.create_user(username="recipient", password="pass")
        self.deal = Deal.objects.create(
            deal_id="deal123",
            game_name="Celeste",
            sale_price=Decimal("9.99"),
            retail_price=Decimal("19.99"),
            thumb_url="http://example.com/thumb.jpg",
            store_name="Epic",
            store_icon_url="http://example.com/icon.jpg",
        )
        self.shared_deal = SharedDeal.objects.create(
            sender=self.sender, recipient=self.recipient, deal=self.deal
        )

    def test_shared_deal_creation(self):
        self.assertEqual(self.shared_deal.sender, self.sender)
        self.assertEqual(self.shared_deal.recipient, self.recipient)
        self.assertEqual(self.shared_deal.deal, self.deal)

    def test_str_representation(self):
        expected = f"{self.sender} shared deal 'Celeste' with {self.recipient}"
        self.assertEqual(str(self.shared_deal), expected)

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            SharedDeal.objects.create(
                sender=self.sender, recipient=self.recipient, deal=self.deal
            )


class SharedReviewModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.recipient = User.objects.create_user(username="recipient", password="pass")
        self.game = Game.objects.create(
            guid="game-1",
            title="Hollow Knight",
            description="A test game",
            genres="Action",
            platforms="PC",
            themes="Theme1",
            image="http://example.com/image.jpg",
            videos="",
            concepts="Concept1",
        )
        self.review = Review.objects.create(
            game=self.game,
            user=self.sender,
            reviewers="Reviewer1",
            review_deck="Short deck",
            review_description="This is a detailed review description.",
            score=4,
            likes=0,
            dislikes=0,
            liked_by="",
            disliked_by="",
            date_added=now(),
        )

        self.shared_review = SharedReview.objects.create(
            sender=self.sender, recipient=self.recipient, review=self.review
        )

    def test_shared_review_creation(self):
        self.assertEqual(self.shared_review.sender, self.sender)
        self.assertEqual(self.shared_review.recipient, self.recipient)
        self.assertEqual(self.shared_review.review, self.review)

    def test_str_representation(self):
        expected = (
            f"{self.sender} shared a review of 'Hollow Knight' with {self.recipient}"
        )
        self.assertEqual(str(self.shared_review), expected)

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            SharedReview.objects.create(
                sender=self.sender, recipient=self.recipient, review=self.review
            )


if __name__ == "__main__":
    import django
    import os
    import sys
    from django.conf import settings

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "playstyle_manager.settings")
    django.setup()

    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_modules"])
    sys.exit(bool(failures))
