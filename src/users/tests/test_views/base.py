import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from users.forms import *
from users.models import *
from django.contrib.auth import SESSION_KEY
from django.contrib.messages import get_messages
from django.urls import reverse
from unittest.mock import patch
from django.shortcuts import redirect

User = get_user_model()