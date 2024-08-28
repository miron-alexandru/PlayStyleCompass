pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@example.com
export DJANGO_SUPERUSER_PASSWORD=adminpassword
python manage.py createsuperuser --noinput