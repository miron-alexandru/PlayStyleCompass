import os
import django
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.playstyle_manager.settings')
django.setup()

def create_superuser(username, email, password):
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
    else:
        print(f"Superuser '{username}' already exists.")

if __name__ == "__main__":
    create_superuser('admin', 'admin@example.com', 'adminpassword')
