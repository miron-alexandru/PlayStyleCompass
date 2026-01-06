import os
import random
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from urllib.parse import urlencode

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.utils.timezone import now, localtime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from playstyle_compass.models import *
from playstyle_compass.forms import *
from playstyle_compass.views import get_filtered_games
from users.models import *
from playstyle_compass.views import (
    genres,
    all_platforms,
    all_themes,
    game_style,
    connection_type,
)