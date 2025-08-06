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


class ChangePasswordDoneTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="StrongPass123!"
        )
        translation.activate("en")
        self.url = reverse("users:change_password_done")

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_view_loads_for_authenticated_user(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/change_succeeded.html")

    def test_context_contains_expected_keys(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertIn("page_title", response.context)
        self.assertIn("response", response.context)
        self.assertIsInstance(response.context["page_title"], str)
        self.assertIsInstance(response.context["response"], str)

    def test_success_message_displayed(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Password Changed Successfully!" in str(m) for m in messages))


class ChangeEmailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="old@example.com", password="StrongPass123!"
        )
        self.url = reverse("users:change_email")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_shows_form_with_email(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/change_email.html")
        self.assertContains(response, "old@example.com")

    def test_post_invalid_shows_errors(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(self.url, data={"new_email": ""}, secure=True)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("new_email", form.errors)

    @override_settings(DEFAULT_FROM_EMAIL="noreply@example.com")
    def test_post_valid_sends_email_and_redirects(self):
        self.client.login(username="testuser", password="StrongPass123!")
        session = self.client.session

        data = {
            "current_password": "StrongPass123!",
            "current_email": self.user.email,
            "new_email": "newemail@example.com",
            "confirm_email": "newemail@example.com",
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:change_email_done"))

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Confirm Email Change", email.subject)
        self.assertIn("newemail@example.com", email.body)
        self.assertEqual(email.to, ["old@example.com"])
        self.assertEqual(email.from_email, "noreply@example.com")

        session = self.client.session
        self.assertEqual(session["email_change_temp"], "newemail@example.com")

        match = re.search(r"/confirm_email_change/\w+/(?P<token>[\w-]+)/", email.body)
        self.assertIsNotNone(match)
        token_from_email = match.group("token")
        self.assertEqual(session["email_change_token"], token_from_email)

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.assertIn(uid, email.body)
        self.assertIn(token_from_email, email.body)


class ChangeEmailDoneTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPass123!",
            email="test@example.com"
        )
        self.url = reverse("users:change_email_done")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_success_page_shows_message(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/change_succeeded.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Confirmation email successfully sent!" in str(m) for m in messages))

        self.assertIn("page_title", response.context)
        self.assertIn("response", response.context)


class ChangeEmailSuccessTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="new@example.com", password="StrongPass123!"
        )
        self.url = reverse("users:change_email_success")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_shows_success_message(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/change_succeeded.html")
        self.assertContains(response, "Email Address successfully changed!")
        self.assertContains(response, self.user.email)


class ConfirmEmailChangeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="old@example.com", password="StrongPass123!"
        )
        self.client.login(username="testuser", password="StrongPass123!")
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse(
            "users:confirm_email_change", kwargs={"uidb64": self.uidb64, "token": self.token}
        )

    def test_invalid_token_returns_error(self):
        session = self.client.session
        session["email_change_token"] = "wrongtoken"
        session["email_change_temp"] = "new@example.com"
        session.save()

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid token for email change.")

    def test_valid_token_changes_email_and_redirects(self):
        session = self.client.session
        session["email_change_token"] = self.token
        session["email_change_temp"] = "new@example.com"
        session.save()

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:change_email_success"))

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

        session = self.client.session
        self.assertNotIn("email_change_token", session)
        self.assertNotIn("email_change_temp", session)


class ChangeLanguageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123!"
        )
        self.url = reverse("users:change_language")
        self.user_profile = self.user.userprofile

    def test_redirect_if_logged_out(self):
        response = self.client.post(self.url, content_type="application/json", secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_fails(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "error"})

    def test_post_invalid_language_no_change(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(
            self.url, '{"language":"fr"}', content_type="application/json", secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.user_profile.refresh_from_db()
        self.assertNotEqual(self.user_profile.language, "fr")

    def test_post_valid_language_changes(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(
            self.url, '{"language":"ro"}', content_type="application/json", secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.language, "ro")
        self.assertEqual(self.client.session["django_language"], "ro")




if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_auth"])
    sys.exit(bool(failures))