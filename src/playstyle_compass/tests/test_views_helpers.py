from django.conf import settings
from django.test import TestCase, RequestFactory, SimpleTestCase
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from collections import defaultdict
from unittest.mock import Mock, patch, MagicMock
from django.http import HttpRequest

from playstyle_compass.helper_functions.views_helpers import *
from django.contrib.auth.models import User
from users.models import FriendList
from playstyle_compass.models import Game, Review, News


class PaginateMatchingGamesTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.sample_games = [f"game_{i}" for i in range(25)]
        self.sample_dict_games = {
            'action': [f"action_game_{i}" for i in range(15)],
            'adventure': [f"adventure_game_{i}" for i in range(12)],
            'puzzle': [f"puzzle_game_{i}" for i in range(8)]
        }
    
    def test_paginate_list_default_page(self):
        """Test pagination with list input and default page (page 1)"""
        request = self.factory.get('/test/')
        result = paginate_matching_games(request, self.sample_games)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 10)
        self.assertEqual(result.number, 1)
        self.assertEqual(list(result)[0], "game_0")
        self.assertEqual(list(result)[-1], "game_9")
    
    def test_paginate_list_specific_page(self):
        """Test pagination with list input and specific page"""
        request = self.factory.get('/test/', {'page': 2})
        result = paginate_matching_games(request, self.sample_games)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 10)
        self.assertEqual(result.number, 2)
        self.assertEqual(list(result)[0], "game_10")
        self.assertEqual(list(result)[-1], "game_19")
    
    def test_paginate_list_last_page(self):
        """Test pagination with list input for last page"""
        request = self.factory.get('/test/', {'page': 3})
        result = paginate_matching_games(request, self.sample_games)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 5)
        self.assertEqual(result.number, 3)
        self.assertEqual(list(result)[0], "game_20")
        self.assertEqual(list(result)[-1], "game_24")
    
    def test_paginate_dict_default_pages(self):
        """Test pagination with dictionary input and default pages"""
        request = self.factory.get('/test/')
        result = paginate_matching_games(request, self.sample_dict_games)
        
        self.assertIsInstance(result, defaultdict)
        self.assertEqual(len(result), 3)

        for category in ['action', 'adventure', 'puzzle']:
            self.assertIn(category, result)
            self.assertIsInstance(result[category], Page)
            self.assertEqual(result[category].number, 1)
    
    def test_paginate_dict_specific_pages(self):
        """Test pagination with dictionary input and specific pages"""
        request = self.factory.get('/test/', {
            'action_page': 2,
            'adventure_page': 1,
            'puzzle_page': 1
        })
        result = paginate_matching_games(request, self.sample_dict_games)
        
        self.assertEqual(result['action'].number, 2)
        self.assertEqual(result['adventure'].number, 1)
        self.assertEqual(result['puzzle'].number, 1)

        action_games = list(result['action'])
        self.assertEqual(len(action_games), 5)
        self.assertEqual(action_games[0], "action_game_10")
        self.assertEqual(action_games[-1], "action_game_14")
    
    def test_paginate_list_invalid_page(self):
        """Test handling of invalid page number with list input"""
        request = self.factory.get('/test/', {'page': 'invalid'})
        result = paginate_matching_games(request, self.sample_games)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result.number, 1)
    
    def test_paginate_list_empty_page(self):
        """Test handling of empty page number with list input"""
        request = self.factory.get('/test/', {'page': 100})
        result = paginate_matching_games(request, self.sample_games)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result.number, 1)
    
    def test_paginate_dict_invalid_page_numbers(self):
        """Test handling of invalid page numbers with dictionary input"""
        request = self.factory.get('/test/', {
            'action_page': 'invalid',
            'adventure_page': 100
        })
        result = paginate_matching_games(request, self.sample_dict_games)

        self.assertEqual(result['action'].number, 1)
        self.assertEqual(result['adventure'].number, 1)
    
    def test_paginate_empty_list(self):
        """Test pagination with empty list"""
        request = self.factory.get('/test/')
        result = paginate_matching_games(request, [])
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 0)
    
    def test_paginate_empty_dict(self):
        """Test pagination with empty dictionary"""
        request = self.factory.get('/test/')
        result = paginate_matching_games(request, {})
        
        self.assertIsInstance(result, defaultdict)
        self.assertEqual(len(result), 0)
    
    def test_paginate_dict_mixed_page_parameters(self):
        """Test pagination with some page parameters missing"""
        request = self.factory.get('/test/', {'action_page': 2})
        result = paginate_matching_games(request, self.sample_dict_games)
        
        self.assertEqual(result['action'].number, 2)
        self.assertEqual(result['adventure'].number, 1)
        self.assertEqual(result['puzzle'].number, 1)
    
    @patch('playstyle_compass.helper_functions.views_helpers.Paginator')
    def test_paginator_exception_handling(self, mock_paginator):
        """Test that exceptions are properly handled"""
        mock_paginator_instance = Mock()
        
        mock_page = Mock()
        mock_page.number = 1
        
        mock_paginator_instance.page.side_effect = [PageNotAnInteger, mock_page]
        
        mock_paginator.return_value = mock_paginator_instance
        
        request = self.factory.get('/test/', {'page': 'invalid'})
        result = paginate_matching_games(request, self.sample_games)
        
        self.assertEqual(result.number, 1)
        self.assertEqual(mock_paginator_instance.page.call_count, 2)
        mock_paginator_instance.page.assert_any_call('invalid')
        mock_paginator_instance.page.assert_any_call(1)
    
    def test_function_signature_and_return_types(self):
        """Test that function accepts correct parameters and returns expected types"""
        request = self.factory.get('/test/')
        
        list_result = paginate_matching_games(request, self.sample_games)
        self.assertIsInstance(list_result, Page)
        
        dict_result = paginate_matching_games(request, self.sample_dict_games)
        self.assertIsInstance(dict_result, defaultdict)
        
        for page in dict_result.values():
            self.assertIsInstance(page, Page)

class GetFriendListTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
    
    @patch('users.views.FriendList.objects.get_or_create')
    def test_get_friend_list_existing(self, mock_get_or_create):
        """Test getting existing friend list"""
        mock_friend1 = Mock()
        mock_friend2 = Mock()
        mock_friends = Mock()
        mock_friends.all.return_value = [mock_friend1, mock_friend2]
        
        mock_friend_list = Mock()
        mock_friend_list.friends = mock_friends

        mock_get_or_create.return_value = (mock_friend_list, False)
        
        result = get_friend_list(self.user)
        
        mock_get_or_create.assert_called_once_with(user=self.user)
        self.assertEqual(result, [mock_friend1, mock_friend2])
    
    @patch('users.views.FriendList.objects.get_or_create')
    def test_get_friend_list_new(self, mock_get_or_create):
        """Test creating new friend list"""
        mock_friends = Mock()
        mock_friends.all.return_value = []
        
        mock_friend_list = Mock()
        mock_friend_list.friends = mock_friends
        
        mock_get_or_create.return_value = (mock_friend_list, True)
        
        result = get_friend_list(self.user)
        
        mock_get_or_create.assert_called_once_with(user=self.user)
        self.assertEqual(result, [])


class CalculateSimilarityTest(TestCase):
    
    def test_calculate_similarity_normal_case(self):
        """Test Jaccard similarity with normal sets"""
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}
        
        result = calculate_similarity(set1, set2)

        expected = 2 / 6
        self.assertAlmostEqual(result, expected)
    
    def test_calculate_similarity_identical_sets(self):
        """Test Jaccard similarity with identical sets"""
        set1 = {1, 2, 3}
        set2 = {1, 2, 3}
        
        result = calculate_similarity(set1, set2)

        expected = 1.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_disjoint_sets(self):
        """Test Jaccard similarity with disjoint sets"""
        set1 = {1, 2, 3}
        set2 = {4, 5, 6}
        
        result = calculate_similarity(set1, set2)

        expected = 0.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_empty_first_set(self):
        """Test Jaccard similarity with empty first set"""
        set1 = set()
        set2 = {1, 2, 3}
        
        result = calculate_similarity(set1, set2)
        
        expected = 0.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_empty_second_set(self):
        """Test Jaccard similarity with empty second set"""
        set1 = {1, 2, 3}
        set2 = set()
        
        result = calculate_similarity(set1, set2)
        
        expected = 0.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_both_empty_sets(self):
        """Test Jaccard similarity with both sets empty"""
        set1 = set()
        set2 = set()
        
        result = calculate_similarity(set1, set2)
        
        expected = 0.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_one_element_sets(self):
        """Test Jaccard similarity with single element sets"""
        set1 = {1}
        set2 = {1}
        
        result = calculate_similarity(set1, set2)
        
        expected = 1.0
        self.assertEqual(result, expected)


class CalculateAverageSimilarityTest(TestCase):
    
    def setUp(self):
        self.user1 = Mock()
        self.user2 = Mock()
        
    def test_calculate_similarity_normal_case(self):
        """Test average similarity calculation with normal preferences"""
        self.user1.genres = "action,adventure,rpg"
        self.user2.genres = "action,rpg,strategy"
        
        self.user1.platforms = "pc,ps5"
        self.user2.platforms = "pc,xbox"
        
        self.user1.themes = "fantasy,sci-fi"
        self.user2.themes = "fantasy,horror"
        
        preferences = ['genres', 'platforms', 'themes']
        
        result = calculate_average_similarity(self.user1, self.user2, preferences)

        expected = (0.5 + 1/3 + 1/3) / 3
        self.assertAlmostEqual(result, expected, places=3)
    
    def test_calculate_similarity_empty_preferences(self):
        """Test average similarity with empty preferences list"""
        preferences = []
        
        result = calculate_average_similarity(self.user1, self.user2, preferences)
        
        self.assertTrue(result == 0 or str(result) == 'nan')
    
    def test_calculate_similarity_empty_user_attributes(self):
        """Test average similarity with empty user attributes"""
        self.user1.genres = ""
        self.user2.genres = "action,rpg"
        
        self.user1.platforms = "pc,ps5"
        self.user2.platforms = ""
        
        preferences = ['genres', 'platforms']
        
        result = calculate_average_similarity(self.user1, self.user2, preferences)

        expected = 0.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_identical_users(self):
        """Test average similarity with identical users"""
        self.user1.genres = "action,adventure"
        self.user2.genres = "action,adventure"
        
        self.user1.platforms = "pc,ps5"
        self.user2.platforms = "pc,ps5"
        
        preferences = ['genres', 'platforms']
        
        result = calculate_average_similarity(self.user1, self.user2, preferences)

        expected = 1.0
        self.assertEqual(result, expected)
    
    def test_calculate_similarity_completely_different(self):
        """Test average similarity with completely different users"""
        self.user1.genres = "action,adventure"
        self.user2.genres = "strategy,puzzle"
        
        self.user1.platforms = "pc,ps5"
        self.user2.platforms = "xbox,mobile"
        
        preferences = ['genres', 'platforms']
        
        result = calculate_average_similarity(self.user1, self.user2, preferences)

        expected = 0.0
        self.assertEqual(result, expected)


class PaginateObjectsTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.sample_objects = [f"object_{i}" for i in range(25)]
    
    def test_paginate_default_page(self):
        """Test pagination with default page"""
        request = self.factory.get('/test/')
        result = paginate_objects(request, self.sample_objects)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 10)
        self.assertEqual(result.number, 1)
        self.assertEqual(list(result)[0], "object_0")
    
    def test_paginate_specific_page(self):
        """Test pagination with specific page"""
        request = self.factory.get('/test/', {'page': 2})
        result = paginate_objects(request, self.sample_objects)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 10)
        self.assertEqual(result.number, 2)
        self.assertEqual(list(result)[0], "object_10")
    
    def test_paginate_custom_objects(self):
        """Test pagination with custom objects per page"""
        request = self.factory.get('/test/')
        result = paginate_objects(request, self.sample_objects, objects_per_page=5)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 5)
        self.assertEqual(result.number, 1)
    
    def test_paginate_invalid_page(self):
        """Test pagination with invalid page number"""
        request = self.factory.get('/test/', {'page': 'invalid'})
        result = paginate_objects(request, self.sample_objects)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result.number, 1)
    
    def test_paginate_empty_page(self):
        """Test pagination with non-existent page"""
        request = self.factory.get('/test/', {'page': 100})
        result = paginate_objects(request, self.sample_objects)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result.number, 1)
    
    def test_paginate_empty_list(self):
        """Test pagination with empty object list"""
        request = self.factory.get('/test/')
        result = paginate_objects(request, [])
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 0)
    
    def test_paginate_single_page(self):
        """Test pagination with objects that fit on one page"""
        few_objects = [f"object_{i}" for i in range(5)]
        request = self.factory.get('/test/')
        result = paginate_objects(request, few_objects)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 5)
        self.assertEqual(result.number, 1)
    
    def test_paginate_last_page(self):
        """Test pagination with last page"""
        request = self.factory.get('/test/', {'page': 3})
        result = paginate_objects(request, self.sample_objects)
        
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 5)
        self.assertEqual(result.number, 3)
        self.assertEqual(list(result)[0], "object_20")


class GatherGameAttributesTest(TestCase):
    
    def setUp(self):
        self.game1 = Game.objects.create(
            title="Game 1",
            guid="1234",
            genres="action,adventure",
            concepts="open world,crafting",
            themes="fantasy,medieval",
            platforms="pc,ps5",
            franchises="elder scrolls",
            description="Test game 1",
            image="image1.jpg",
            videos="video1.mp4"
        )
        
        self.game2 = Game.objects.create(
            title="Game 2",
            guid="4329",
            genres="rpg,action",
            concepts="crafting,multiplayer",
            themes="sci-fi,futuristic",
            platforms="xbox,pc",
            franchises="mass effect",
            description="Test game 2",
            image="image2.jpg",
            videos="video2.mp4"
        )
        
        self.game3 = Game.objects.create(
            title="Game 3",
            genres="",
            concepts="",
            themes="horror",
            platforms="switch",
            franchises="",
            description="Test game 3",
            image="image3.jpg",
            videos="video3.mp4"
        )
    
    def test_normal_case(self):
        games = [self.game1, self.game2]
        result = gather_game_attributes(games)
        
        expected_genres = {"action", "adventure", "rpg"}
        expected_concepts = {"open world", "crafting", "multiplayer"}
        expected_themes = {"fantasy", "medieval", "sci-fi", "futuristic"}
        expected_platforms = {"pc", "ps5", "xbox"}
        expected_franchises = {"elder scrolls", "mass effect"}
        
        self.assertEqual(result[0], expected_genres)
        self.assertEqual(result[1], expected_concepts)
        self.assertEqual(result[2], expected_themes)
        self.assertEqual(result[3], expected_platforms)
        self.assertEqual(result[4], expected_franchises)
    
    def test_empty_fields(self):
        games = [self.game3]
        result = gather_game_attributes(games)
        
        expected_genres = set()
        expected_concepts = set()
        expected_themes = {"horror"}
        expected_platforms = {"switch"}
        expected_franchises = set()
        
        self.assertEqual(result[0], expected_genres)
        self.assertEqual(result[1], expected_concepts)
        self.assertEqual(result[2], expected_themes)
        self.assertEqual(result[3], expected_platforms)
        self.assertEqual(result[4], expected_franchises)
    
    def test_mixed_games(self):
        games = [self.game1, self.game2, self.game3]
        result = gather_game_attributes(games)
        
        expected_genres = {"action", "adventure", "rpg"}
        expected_concepts = {"open world", "crafting", "multiplayer"}
        expected_themes = {"fantasy", "medieval", "sci-fi", "futuristic", "horror"}
        expected_platforms = {"pc", "ps5", "xbox", "switch"}
        expected_franchises = {"elder scrolls", "mass effect"}
        
        self.assertEqual(result[0], expected_genres)
        self.assertEqual(result[1], expected_concepts)
        self.assertEqual(result[2], expected_themes)
        self.assertEqual(result[3], expected_platforms)
        self.assertEqual(result[4], expected_franchises)
    
    def test_empty_list(self):
        games = []
        result = gather_game_attributes(games)
        
        self.assertEqual(result[0], set())
        self.assertEqual(result[1], set())
        self.assertEqual(result[2], set())
        self.assertEqual(result[3], set())
        self.assertEqual(result[4], set())
    
    def test_whitespace_handling(self):
        game = Game.objects.create(
            title="Game with whitespace",
            guid="2314",
            genres=" action , adventure ",
            concepts="open world, crafting ",
            themes=" fantasy, medieval ",
            platforms=" pc , ps5 ",
            franchises=" elder scrolls ",
            description="Test game",
            image="image.jpg",
            videos="video.mp4"
        )
        
        result = gather_game_attributes([game])
        
        expected_genres = {" action ", " adventure "}
        expected_concepts = {"open world", " crafting "}
        expected_themes = {" fantasy", " medieval "}
        expected_platforms = {" pc ", " ps5 "}
        expected_franchises = {" elder scrolls "}
        
        self.assertEqual(result[0], expected_genres)
        self.assertEqual(result[1], expected_concepts)
        self.assertEqual(result[2], expected_themes)
        self.assertEqual(result[3], expected_platforms)
        self.assertEqual(result[4], expected_franchises)
    
    def test_null_fields(self):
        game = Game.objects.create(
            title="Game with null fields",
            guid="2342",
            genres="strategy",
            concepts="",
            themes="",
            platforms="pc",
            franchises="",
            description="Test game",
            image="image.jpg",
            videos="video.mp4"
        )
        
        result = gather_game_attributes([game])
        
        expected_genres = {"strategy"}
        expected_concepts = set()
        expected_themes = set()
        expected_platforms = {"pc"}
        expected_franchises = set()
        
        self.assertEqual(result[0], expected_genres)
        self.assertEqual(result[1], expected_concepts)
        self.assertEqual(result[2], expected_themes)
        self.assertEqual(result[3], expected_platforms)
        self.assertEqual(result[4], expected_franchises)


class BuildQueryTest(TestCase):
    
    def test_build_query_with_filters(self):
        selected_filters = {
            "genres": ["action", "rpg"],
            "platforms": ["pc"],
            "themes": []
        }
        
        result = build_query(selected_filters)
        
        self.assertIsInstance(result, Q)
        self.assertTrue(result.children)
    
    def test_build_query_empty_filters(self):
        selected_filters = {
            "genres": [],
            "platforms": [],
            "themes": []
        }
        
        result = build_query(selected_filters)
        
        self.assertIsInstance(result, Q)
        self.assertFalse(result.children)
    
    def test_build_query_mixed_filters(self):
        selected_filters = {
            "genres": ["action"],
            "platforms": [],
            "themes": ["fantasy"],
            "concepts": ["open world"]
        }
        
        result = build_query(selected_filters)
        
        self.assertIsInstance(result, Q)
        self.assertTrue(result.children)
    
    def test_build_query_single_filter(self):
        selected_filters = {
            "genres": ["action"]
        }
        
        result = build_query(selected_filters)
        
        self.assertIsInstance(result, Q)
        self.assertTrue(result.children)


class GetSelectedFiltersTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_filters_from_request(self):
        request = self.factory.get('/?genres=action&genres=rpg&platforms=pc')
        
        result = get_selected_filters(request)
        
        expected = {
            "genres": ["action", "rpg"],
            "concepts": [],
            "themes": [],
            "platforms": ["pc"],
            "franchises": []
        }
        self.assertEqual(result, expected)
    
    def test_get_filters_empty_request(self):
        request = self.factory.get('/')
        
        result = get_selected_filters(request)
        
        expected = {
            "genres": [],
            "concepts": [],
            "themes": [],
            "platforms": [],
            "franchises": []
        }
        self.assertEqual(result, expected)
    
    def test_get_filters_all_types(self):
        request = self.factory.get('/?genres=action&concepts=crafting&themes=fantasy&platforms=pc&franchises=zelda')
        
        result = get_selected_filters(request)
        
        expected = {
            "genres": ["action"],
            "concepts": ["crafting"],
            "themes": ["fantasy"],
            "platforms": ["pc"],
            "franchises": ["zelda"]
        }
        self.assertEqual(result, expected)


class SortGameLibraryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="12345")

        self.game1 = Game.objects.create(
            title="B Game",
            guid="314",
            release_date="2023-01-01",
            description="Test",
            image="test.jpg",
            videos="test.mp4",
            genres="action",
            platforms="pc",
            concepts="test",
        )
        self.game2 = Game.objects.create(
            title="A Game",
            guid="34122",
            release_date="2022-01-01",
            description="Test",
            image="test.jpg",
            videos="test.mp4",
            genres="action",
            platforms="pc",
            concepts="test",
        )
        self.game3 = Game.objects.create(
            title="C Game",
            guid="2314",
            release_date="2024-01-01",
            description="Test",
            image="test.jpg",
            videos="test.mp4",
            genres="action",
            platforms="pc",
            concepts="test",
        )

        Review.objects.create(
            game=self.game1, user=self.user, reviewers="R1",
            review_deck="Deck1", review_description="desc", score=8
        )
        Review.objects.create(
            game=self.game1, user=self.user, reviewers="R2",
            review_deck="Deck2", review_description="desc", score=9
        )
        Review.objects.create(
            game=self.game2, user=self.user, reviewers="R3",
            review_deck="Deck3", review_description="desc", score=9
        )
        Review.objects.create(
            game=self.game3, user=self.user, reviewers="R4",
            review_deck="Deck4", review_description="desc", score=7
        )
        Review.objects.create(
            game=self.game3, user=self.user, reviewers="R5",
            review_deck="Deck5", review_description="desc", score=8
        )

        for g in [self.game1, self.game2, self.game3]:
            g.update_score()

        self.games = Game.objects.all()
    
    def test_sort_by_title_asc(self):
        result = sort_game_library(self.games, "title_asc")
        titles = list(result.values_list('title', flat=True))
        self.assertEqual(titles, ["A Game", "B Game", "C Game"])
    
    def test_sort_by_title_desc(self):
        result = sort_game_library(self.games, "title_desc")
        titles = list(result.values_list('title', flat=True))
        self.assertEqual(titles, ["C Game", "B Game", "A Game"])
    
    def test_sort_by_release_date_asc(self):
        result = sort_game_library(self.games, "release_date_asc")
        dates = list(result.values_list('release_date', flat=True))
        self.assertEqual(dates, ["2022-01-01", "2023-01-01", "2024-01-01"])
    
    def test_sort_by_release_date_desc(self):
        result = sort_game_library(self.games, "release_date_desc")
        dates = list(result.values_list('release_date', flat=True))
        self.assertEqual(dates, ["2024-01-01", "2023-01-01", "2022-01-01"])
    
    def test_sort_by_score_asc(self):
        result = sort_game_library(self.games, "average_score_asc")
        scores = list(result.values_list('average_score', flat=True))
        self.assertEqual(scores, [7.5, 8.5, 9.0])
    
    def test_sort_by_score_desc(self):
        result = sort_game_library(self.games, "average_score_desc")
        scores = list(result.values_list('average_score', flat=True))
        self.assertEqual(scores, [9.0, 8.5, 7.5])
    
    def test_sort_default(self):
        result = sort_game_library(self.games, "invalid_sort")
        self.assertEqual(result.count(), 3)


class GetUserContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="12345")
        self.friend = User.objects.create_user(username="friend", password="12345")
        self.preferences = self.user.userpreferences

    def test_anonymous_user(self):
        request = self.factory.get("/")
        request.user = type("Anonymous", (), {"is_authenticated": False})()
        user, prefs, friends = get_user_context(request)

        self.assertIsNone(user)
        self.assertIsNone(prefs)
        self.assertEqual(list(friends), [])

    def test_authenticated_user_without_friends(self):
        request = self.factory.get("/")
        request.user = self.user
        user, prefs, friends = get_user_context(request)

        self.assertEqual(user, self.user)
        self.assertEqual(prefs, self.preferences)
        self.assertEqual(list(friends), [])

    def test_authenticated_user_with_friends(self):
        friend_list, _ = FriendList.objects.get_or_create(user=self.user)
        friend_list.friends.add(self.friend)

        request = self.factory.get("/")
        request.user = self.user
        user, prefs, friends = get_user_context(request)

        self.assertEqual(user, self.user)
        self.assertEqual(prefs, self.preferences)
        self.assertIn(self.friend, list(friends))


class GetAssociatedPlatformsTests(TestCase):
    def setUp(self):
        self.n1 = News.objects.create(title="N1", platforms="PC, PS5")
        self.n2 = News.objects.create(title="N2", platforms="Switch, PC")
        self.n3 = News.objects.create(title="N3", platforms=None)

    def test_single_news_platforms(self):
        result = get_associated_platforms([self.n1])
        self.assertEqual(result, {"PC", "PS5"})

    def test_multiple_news_with_overlap(self):
        result = get_associated_platforms([self.n1, self.n2])
        self.assertEqual(result, {"PC", "PS5", "Switch"})

    def test_news_with_no_platforms(self):
        result = get_associated_platforms([self.n3])
        self.assertEqual(result, set())

    def test_platforms_strip_whitespace(self):
        article = News.objects.create(title="N4", platforms=" PC , Xbox ")
        result = get_associated_platforms([article])
        self.assertEqual(result, {"PC", "Xbox"})



class SortArticlesTests(TestCase):
    def setUp(self):
        self.n1 = News.objects.create(
            title="B Article", publish_date="2023-01-01", platforms="PC"
        )
        self.n2 = News.objects.create(
            title="A Article", publish_date="2022-01-01", platforms="PC"
        )
        self.n3 = News.objects.create(
            title="C Article", publish_date="2024-01-01", platforms="PC"
        )
        self.articles = News.objects.all()

    def test_sort_by_publish_date_asc(self):
        result = sort_articles(self.articles, "publish_date_asc")
        self.assertEqual(list(result), [self.n2, self.n1, self.n3])

    def test_sort_by_publish_date_desc(self):
        result = sort_articles(self.articles, "publish_date_desc")
        self.assertEqual(list(result), [self.n3, self.n1, self.n2])

    def test_sort_by_title_asc(self):
        result = sort_articles(self.articles, "title_asc")
        self.assertEqual(list(result), [self.n2, self.n1, self.n3])

    def test_sort_by_title_desc(self):
        result = sort_articles(self.articles, "title_desc")
        self.assertEqual(list(result), [self.n3, self.n1, self.n2])

    def test_sort_default(self):
        result = sort_articles(self.articles, "invalid")
        self.assertEqual(result.count(), 3)


class GetSimilarGamesTests(TestCase):
    def setUp(self):
        self.main_game = Game.objects.create(
            guid="1",
            title="Main Game",
            description="Test",
            genres="action,strategy",
            themes="sci-fi",
            concepts="survival",
            platforms="pc,ps5",
            developers="dev1",
            image="test.jpg",
            videos="test.mp4",
        )

        self.game1 = Game.objects.create(
            guid="2",
            title="Similar Game 1",
            description="Test",
            genres="action",
            themes="fantasy",
            concepts="puzzle",
            platforms="pc",
            developers="dev1",
            image="test.jpg",
            videos="test.mp4",
        )

        self.game2 = Game.objects.create(
            guid="3",
            title="Similar Game 2",
            description="Test",
            genres="rpg",
            themes="sci-fi",
            concepts="survival",
            platforms="xbox",
            developers="dev2",
            image="test.jpg",
            videos="test.mp4",
        )

        self.game3 = Game.objects.create(
            guid="4",
            title="Similar Game 3",
            description="Test",
            genres="action,strategy",
            themes="sci-fi",
            concepts="survival",
            platforms="pc,ps5",
            developers="dev1",
            image="test.jpg",
            videos="test.mp4",
        )

        self.game4 = Game.objects.create(
            guid="5",
            title="Unrelated Game",
            description="Test",
            genres="rpg",
            themes="fantasy",
            concepts="puzzle",
            platforms="xbox",
            developers="dev2",
            image="test.jpg",
            videos="test.mp4",
        )

    def test_default_min_matching_attributes(self):
        result = get_similar_games(self.main_game)
        self.assertIn(self.game1, result)
        self.assertIn(self.game3, result)
        self.assertNotIn(self.game2, result)
        self.assertNotIn(self.game4, result)

    def test_lower_min_matching_attributes(self):
        result = get_similar_games(self.main_game, min_matching_attributes=2)
        self.assertIn(self.game1, result)
        self.assertIn(self.game2, result)
        self.assertIn(self.game3, result)
        self.assertNotIn(self.game4, result)

    def test_higher_min_matching_attributes(self):
        result = get_similar_games(self.main_game, min_matching_attributes=4)
        self.assertIn(self.game3, result)
        self.assertNotIn(self.game1, result)
        self.assertNotIn(self.game2, result)
        self.assertNotIn(self.game4, result)


class GetFirstLetterTests(SimpleTestCase):
    def test_returns_first_alpha_character(self):
        self.assertEqual(get_first_letter("123Game"), "G")
        self.assertEqual(get_first_letter("!@#Hello"), "H")

    def test_returns_uppercase_letter(self):
        self.assertEqual(get_first_letter("apple"), "A")

    def test_returns_hash_if_no_alpha(self):
        self.assertEqual(get_first_letter("12345"), "#")
        self.assertEqual(get_first_letter(""), "#")
        self.assertEqual(get_first_letter("!@#$%"), "#")


class RecommendationEngineTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="pass")

        self.preferences = self.user.userpreferences

        self.preferences.gaming_history = "History Game"
        self.preferences.favorite_genres = "action"
        self.preferences.themes = "sci-fi"
        self.preferences.platforms = "pc"
        self.preferences.game_styles = "Multiplayer"
        self.preferences.connection_types = "Online"
        self.preferences.save()

        self.history_game = Game.objects.create(
            guid="g1",
            title="History Game",
            description="",
            genres="action",
            themes="sci-fi",
            concepts="survival",
            platforms="pc",
            developers="dev1",
            release_date="2020-01-01",
            image="x.jpg",
            videos="x.mp4",
        )

        self.future_game = Game.objects.create(
            guid="g2",
            title="Future Action Game",
            description="",
            genres="action",
            themes="sci-fi",
            concepts="survival",
            platforms="pc",
            developers="dev1",
            release_date=str(date.today().year + 1) + "-01-01",
            image="x.jpg",
            videos="x.mp4",
        )

        self.other_game = Game.objects.create(
            guid="g3",
            title="Other Game",
            description="",
            genres="rpg",
            themes="fantasy",
            concepts="puzzle",
            platforms="xbox",
            developers="dev2",
            release_date="2019-01-01",
            image="x.jpg",
            videos="x.mp4",
        )

    def test_process_generates_recommendations(self):
        request = self.factory.get("/")
        request.user = self.user

        engine = RecommendationEngine(request, self.preferences)
        engine.process()
        results = engine.matching_games

        history_titles = [g.title for g in results["gaming_history"]]
        self.assertIn("History Game", history_titles)
        self.assertNotIn("Future Action Game", history_titles)

        genre_titles = [g.title for g in results["favorite_genres"]]
        self.assertIn("History Game", genre_titles)

        theme_titles = [g.title for g in results["themes"]]
        self.assertIn("History Game", theme_titles)

        platform_titles = [g.title for g in results["preferred_platforms"]]
        self.assertIn("History Game", platform_titles)

        playstyle_titles = [g.title for g in results["playstyle_games"]]
        self.assertIn("History Game", playstyle_titles)

    def test_sorting_changes_order(self):
        request = self.factory.get("/?sort=title_desc")
        request.user = self.user

        engine = RecommendationEngine(request, self.preferences)
        engine.process()
        results = engine.matching_games

        for category, games in results.items():
            if games:
                titles = [g.title for g in games]
                self.assertEqual(titles, sorted(titles, reverse=True))
