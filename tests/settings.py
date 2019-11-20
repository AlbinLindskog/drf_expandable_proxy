import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'not-very-secret-buz-tests'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tests.test_app.apps.TestAppConfig'
]

MIDDLEWARE = []

ROOT_URLCONF = 'urls'

TEMPLATES = []

WSGI_APPLICATION = 'tests.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}