"""Django settings for Targem Games adaptation system."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR.parent / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local apps
    'users',
    'adaptation',
    'knowledge',
    'assistant',
    'trainer',
    'gamification',
    'monitoring',
    'admin_panel',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'targem_db'),
        'USER': os.getenv('DB_USER', 'targem_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# External services (Ollama, Chroma)
CHROMA_HOST = os.getenv('CHROMA_HOST', 'chroma')
CHROMA_PORT = int(os.getenv('CHROMA_PORT', '8000'))
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'host.docker.internal')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', '11434'))
OLLAMA_URL = f'http://{OLLAMA_HOST}:{OLLAMA_PORT}'

LM_STUDIO_HOST = os.getenv('LM_STUDIO_HOST', '127.0.0.1')
LM_STUDIO_PORT = int(os.getenv('LM_STUDIO_PORT', '1234'))
LM_STUDIO_URL = f'http://{LM_STUDIO_HOST}:{LM_STUDIO_PORT}'
