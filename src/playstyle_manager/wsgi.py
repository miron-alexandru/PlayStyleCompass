import os

from django.core.wsgi import get_wsgi_application

# Set the environment variable to indicate production mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Get the Django WSGI application
application = get_wsgi_application()
