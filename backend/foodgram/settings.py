import os

import rest_framework.permissions
from dotenv import load_dotenv
from pathlib import Path

from users.setup import DJOSER, SIMPLE_JWT


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-f*uc(csx95l66++$&vf2(bamo1ejsa837lo)z7+v&=82cajrft'
)

load_dotenv(os.path.join(BASE_DIR, '.env_db'))
load_dotenv(os.path.join(BASE_DIR, '.env_mail'))
load_dotenv(os.path.join(BASE_DIR, '.env_web'))

DEBUG = False

# ALLOWED_HOSTS = [
#     '192.168.0.104', 'localhost', '127.0.0.1', '.zhss.tk', 'www.zhss.tk'
# ]

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'users.apps.UsersConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'foodgram_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'foodgram_16147'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'users.pagination.LimitPageNumberPagination',
    'PAGE_SIZE': 6,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
#STATICFILES_DIRS = [BASE_DIR / 'api/static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIN_WIDTH, MIN_HEIGHT = 480, 169

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.mail.ru')
    EMAIL_PORT = os.environ.get('EMAIL_PORT', 2525)
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'zhss.83@mail.ru')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'xxxxxxxxxxxx')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', False)
    SERVER_EMAIL = os.environ.get('EMAIL_HOST_USER', 'zhss.83@mail.ru')
    DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', 'zhss.83@mail.ru')

EMAIL_FOODGRAM = os.environ.get('EMAIL_FOODGRAM', 'zhss.83@mail.ru')
