import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from collections import defaultdict
from unittest.mock import Mock, patch, MagicMock
from django.http import HttpRequest

from playstyle_compass.helper_functions.views_helpers import *
from django.contrib.auth.models import User
from users.models import FriendList


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
        
        # Check action page 2 has correct items
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
        
        # Both should fall back to page 1
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



if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views_helpers"])
    sys.exit(bool(failures))