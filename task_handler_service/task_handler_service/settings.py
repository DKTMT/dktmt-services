"""
Django settings for task_handler_service project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Load the variables from the environment variable
APP_SECRET = os.environ.get("TASK_HANDLER_SERVICE_APP_SECRET")
DB_HOST = os.environ.get("TASK_HANDLER_SERVICE_DB_HOST")
DB_PORT = os.environ.get("TASK_HANDLER_SERVICE_DB_PORT")
DB_NAME = os.environ.get("TASK_HANDLER_SERVICE_DB_NAME")
DB_USERNAME = os.environ.get("TASK_HANDLER_SERVICE_DB_USERNAME")
DB_PASSWORD = os.environ.get("TASK_HANDLER_SERVICE_DB_PASSWORD")
HOSTS = os.environ.get("TASK_HANDLER_SERVICE_ALLOWED_HOSTS").split(' ')

AUTH_SERVICE_HOST = os.environ.get("AUTH_SERVICE_HOST")
AUTH_SERVICE_PORT = os.environ.get("AUTH_SERVICE_PORT")
PREDICT_SERVICE_HOST = os.environ.get("PREDICT_SERVICE_HOST")
PREDICT_SERVICE_PORT = os.environ.get("PREDICT_SERVICE_PORT")
EXCHANGE_SERVICE_HOST = os.environ.get("EXCHANGE_SERVICE_HOST")
EXCHANGE_SERVICE_PORT = os.environ.get("EXCHANGE_SERVICE_PORT")

ENCRYPTION_KEY = os.environ.get("EXCHANGE_SERVICE_ENCRYPTION_KEY")
PUBLIC_KEY = os.environ.get("EXCHANGE_SERVICE_PUBLIC_KEY")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = APP_SECRET

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = HOSTS

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_apscheduler",
    "django_celery_results",
    "django_celery_beat",
    "tasks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "task_handler_service.middleware.OAuthValidationMiddleware",
]

ROOT_URLCONF = "task_handler_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "task_handler_service.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USERNAME,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_DB_TABLES = {'task': 'celery_taskmeta'}
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"