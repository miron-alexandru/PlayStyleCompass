"""WSGI config for PlayStyle Compass."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pslaystyle_manager.settings')

application = get_wsgi_application()
