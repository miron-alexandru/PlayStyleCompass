from .base import *


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.login_url = reverse("users:login")
        self.redirect_url = reverse("playstyle_compass:index")
        User.objects.create_user(username="testuser", password="strongpassword123")

    def test_redirect_if_logged_in(self):
        self.client.login(username="testuser", password="strongpassword123")
        response = self.client.get(self.login_url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.redirect_url)

    def test_remember_me_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "strongpassword123",
                "remember_me": True,
            },
            secure=True
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get(SESSION_KEY))
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)
    def test_session_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "strongpassword123",
                "remember_me": False,
            },
            secure=True
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get(SESSION_KEY))
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_wrong_credentials(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
            secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect username or password")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.logout_url = reverse("users:logout")
        self.user = User.objects.create_user(username="testuser", password="strongpassword123")

    def test_logout_clears_session(self):
        self.client.login(username="testuser", password="strongpassword123")
        self.assertIn(SESSION_KEY, self.client.session)

        response = self.client.get(self.logout_url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/logged_out.html")
        self.assertNotIn(SESSION_KEY, self.client.session)


class ResendActivationLinkTest(TestCase):
    def setUp(self):
        self.url = reverse("users:resend_activation_link")
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="strongpass123")

    def test_get_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 405)

    def test_login_required(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    @patch("users.views.activate_email")
    def test_post_calls_activate_email(self, mock_activate_email):
        self.client.force_login(self.user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        mock_activate_email.assert_called_once()
        args, kwargs = mock_activate_email.call_args
        self.assertEqual(args[1], self.user)
        self.assertEqual(args[2], self.user.email)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.url = reverse("users:register")

    def test_redirect_if_authenticated(self):
        User.objects.create_user(username="testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("playstyle_compass:index"))

    def test_get_renders_form(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertContains(response, "Register")

    @patch("users.views.register_user")
    @patch("users.forms.ReCaptchaField.clean", return_value=None)
    def test_post_calls_register_user(self, mock_captcha_clean, mock_register_user):
        data = {
            "username": "newuser",
            "password1": "StrongPass1@",
            "password2": "StrongPass1@",
            "email": "newuser@example.com",
            "profile_name": "NewProfile123",
        }
        mock_register_user.return_value = redirect("playstyle_compass:index")
        response = self.client.post(self.url, data, secure=True)
        self.assertTrue(mock_register_user.called)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("playstyle_compass:index"))

    def test_post_invalid_rerenders_form(self):
        data = {
            "username": "baduser",
            "password1": "pass",
            "password2": "pass_diff",
        }
        response = self.client.post(self.url, data, secure=True)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("password2", form.errors)
        self.assertIn("The two password fields didn’t match.", form.errors["password2"])


class ChangePasswordTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Oldpass123!")
        self.url = reverse("users:change_password")
        self.done_url = reverse("users:change_password_done")
        self.client.login(username="testuser", password="Oldpass123!")

    def test_get_shows_form(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_post_valid_new_password_changes_password(self):
        data = {
            "old_password": "Oldpass123!",
            "new_password1": "Str0ngPass!@",
            "new_password2": "Str0ngPass!@",
        }
        response = self.client.post(self.url, data, secure=True)
        self.assertIn(response.status_code, [301, 302])
        self.assertEqual(response.url, self.done_url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Str0ngPass!@"))


    def test_post_same_new_password_shows_error(self):
        data = {
            "old_password": "Oldpass123!",
            "new_password1": "Oldpass123!",
            "new_password2": "Oldpass123!",
        }
        response = self.client.post(self.url, data, secure=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("different from the old password" in str(m) for m in messages))
        self.assertEqual(response.status_code, 200)

    def test_post_non_matching_new_passwords_adds_form_error(self):
        data = {
            "old_password": "Oldpass123!",
            "new_password1": "Newpass123!",
            "new_password2": "Mismatch123!",
        }
        response = self.client.post(self.url, data, secure=True)
        form = response.context["form"]
        self.assertTrue(form.errors.get("new_password2"))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_auth"])
    sys.exit(bool(failures))