import os
import sys
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from users.forms import *
from users.models import *
from playstyle_compass.models import Review, Game
from django.contrib.auth import SESSION_KEY
from django.contrib.messages import get_messages
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.shortcuts import redirect
from django.core import mail
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import translation, timezone
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from users.tokens import account_deletion_token
from datetime import timedelta


User = get_user_model()