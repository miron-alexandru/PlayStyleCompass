from ..base import *


class ViewFranchisesViewTest(TestCase):
    def setUp(self):
        self.url = reverse("playstyle_compass:view_franchises")
        Franchise.objects.create(title="Zelda", games_count=10)
        Franchise.objects.create(title="Mario", games_count=5)
        Franchise.objects.create(title="Metroid", games_count=7)

    def test_view_loads(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/franchise_list.html")

    def test_shows_all_franchises(self):
        response = self.client.get(self.url, secure=True)
        franchises = response.context["franchises"].object_list
        self.assertEqual(len(franchises), 3)

    def test_sorts_alphabetically_ascending(self):
        response = self.client.get(self.url + "?sort_order=asc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        titles = [f.title for f in franchises]
        self.assertEqual(titles, sorted(titles))

    def test_sorts_alphabetically_descending(self):
        response = self.client.get(self.url + "?sort_order=desc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        titles = [f.title for f in franchises]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_sorts_by_games_count_ascending(self):
        response = self.client.get(self.url + "?sort_order=games_asc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        games_counts = [f.games_count for f in franchises]
        self.assertEqual(games_counts, sorted(games_counts))

    def test_sorts_by_games_count_descending(self):
        response = self.client.get(self.url + "?sort_order=games_desc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        games_counts = [f.games_count for f in franchises]
        self.assertEqual(games_counts, sorted(games_counts, reverse=True))


class ViewFranchiseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.franchise = Franchise.objects.create(title="Awesome Franchise", games_count=5)
        self.url = reverse("playstyle_compass:franchise", args=[self.franchise.id])

    def test_can_view_franchise(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/view_franchise.html")
        franchise = response.context["franchise"]
        self.assertEqual(franchise, self.franchise)
        self.assertIn(self.franchise.title, response.context["page_title"])

    def test_404_if_not_found(self):
        invalid_url = reverse("playstyle_compass:franchise", args=[999])
        response = self.client.get(invalid_url, secure=True)
        self.assertEqual(response.status_code, 404)


class ViewCharactersViewTest(TestCase):
    def setUp(self):
        self.char1 = Character.objects.create(name="Alpha Character")
        self.char2 = Character.objects.create(name="Bravo Character")
        self.char3 = Character.objects.create(name="Charlie Character")
        self.url = reverse("playstyle_compass:characters")

    def test_shows_all_characters(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "characters/characters.html")
        characters = list(response.context["characters"])
        self.assertEqual(len(characters), 3)

    def test_sorts_characters_ascending(self):
        response = self.client.get(self.url + "?sort_order=asc", secure=True)
        characters = list(response.context["characters"])
        names = [c.name for c in characters]
        self.assertEqual(names, sorted(names))

    def test_sorts_characters_descending(self):
        response = self.client.get(self.url + "?sort_order=desc", secure=True)
        characters = list(response.context["characters"])
        names = [c.name for c in characters]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_invalid_sort_order_defaults(self):
        response = self.client.get(self.url + "?sort_order=invalid", secure=True)
        self.assertEqual(response.status_code, 200)
        characters = list(response.context["characters"])
        self.assertEqual(len(characters), 3)


class GameCharacterViewTest(TestCase):
    def setUp(self):
        self.character = Character.objects.create(name="Test Character")
        self.url = reverse("playstyle_compass:character", args=[self.character.id])

    def test_shows_character_page(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "characters/game_character.html")
        self.assertEqual(response.context["character"], self.character)
        self.assertContains(response, self.character.name)

    def test_returns_404_for_missing_character(self):
        url = reverse("playstyle_compass:character", args=[9999])
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 404)


class SearchCharactersViewTest(TestCase):
    def setUp(self):
        self.character1 = Character.objects.create(name="Aloy")
        self.character2 = Character.objects.create(name="Arthur Morgan")
        self.url = reverse("playstyle_compass:search_characters")

    def test_can_find_character(self):
        response = self.client.get(self.url, {"query": "Aloy"}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "characters/search_characters.html")
        characters = response.context["characters"]
        self.assertIn(self.character1, characters)
        self.assertNotIn(self.character2, characters)
        self.assertContains(response, "Aloy")

    def test_short_query_is_bad(self):
        response = self.client.get(self.url, {"query": "A"}, secure=True)
        self.assertEqual(response.status_code, 400)

    def test_empty_results(self):
        response = self.client.get(self.url, {"query": "NothingHere"}, secure=True)
        self.assertEqual(response.status_code, 200)
        characters = response.context["characters"]
        self.assertEqual(len(characters), 0)


class AutocompleteCharactersViewTest(TestCase):
    def setUp(self):
        self.character1 = Character.objects.create(name="Aloy")
        self.character2 = Character.objects.create(name="Arthur Morgan")
        self.character3 = Character.objects.create(name="Kratos")
        self.url = reverse("playstyle_compass:autocomplete_characters")

    def test_returns_matches(self):
        response = self.client.get(self.url, {"query": "Ar"}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = [item["name"] for item in data["results"]]
        self.assertIn("Arthur Morgan", results)
        self.assertNotIn("Aloy", results)
        self.assertNotIn("Kratos", results)

    def test_returns_empty_when_no_match(self):
        response = self.client.get(self.url, {"query": "Zelda"}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], [])

    def test_returns_empty_for_blank_query(self):
        response = self.client.get(self.url, {"query": ""}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], [])


class SearchFranchisesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:search_franchises')

        self.franchise = Franchise.objects.create(title="The Legend of Zelda")

    def test_valid_search_query_real_render(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "Zelda"}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/search_franchises.html")
        self.assertContains(response, "The Legend of Zelda")

    def test_search_with_no_results(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "UnknownFranchise"}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/search_franchises.html")
        self.assertContains(response, "UnknownFranchise")
        self.assertEqual(len(response.context["franchises"].object_list), 0)

    def test_query_too_short_returns_400(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "A"}, secure=True)

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid query", status_code=400)

    def test_empty_query_renders_page(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": ""}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/search_franchises.html")
        self.assertEqual(response.context["query"], "")


class AutocompleteFranchisesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:autocomplete_franchises')
        Franchise.objects.create(title="The Legend of Zelda")
        Franchise.objects.create(title="The Witcher")

    def test_autocomplete_returns_matching_franchises(self):
        response = self.client.get(self.url, {"query": "The"}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        titles = [item["title"] for item in data["results"]]

        self.assertIn("The Legend of Zelda", titles)
        self.assertIn("The Witcher", titles)

    def test_autocomplete_returns_no_matches(self):
        response = self.client.get(self.url, {"query": "Mario"}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["results"], [])

    def test_autocomplete_empty_query_returns_empty_list(self):
        response = self.client.get(self.url, {"query": ""}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["results"], [])
