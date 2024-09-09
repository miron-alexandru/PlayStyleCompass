"""Defines tokens."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Account activation token."""

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


class AccountDeletionTokenGenerator(PasswordResetTokenGenerator):
    """Account deletion token."""

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
            + six.text_type(user.userprofile.email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()
account_deletion_token = AccountDeletionTokenGenerator()
