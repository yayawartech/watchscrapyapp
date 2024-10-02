"""
Django settings for WatchInfo project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

# from storages.backends.s3boto3 import S3Boto3Storage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "oigyE&A=PM!F!C1IlhsXfWp10dQqoJrkasB#fN*07(MvS#D6D0"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") or False
if DEBUG:
    ALLOWED_HOSTS = ["*"]  # for development purpose only
else:
    ALLOWED_HOSTS = ["165.22.181.81"]  # for production (put production server's ip or domain )


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "base_objects",
    "goldapp",
    "django_crontab",
    "diamondsapp",
    "watchapp",
    # Put your new apps here!
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "WatchInfo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"),],
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

WSGI_APPLICATION = "WatchInfo.wsgi.application"

LOGIN_URL = "/"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
        'awsrds': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'rds.sqlite3'),
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
        'awsrds': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('RDS_DB_NAME'),
            'USER': os.getenv('RDS_USER'),
            'PASSWORD': os.getenv('RDS_PASSWORD'),
            'HOST': os.getenv('RDS_HOST'),
            'PORT': os.getenv('RDS_PORT'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        },
    }

DATABASE_ROUTERS = ['watchapp.routers.AwsRdsRouter',
                    'WatchInfo.routers.DefaultRouter',]


# Configure Amazon S3 settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')


CRONJOBS = [
    ('30 * * * *', 'goldapp.cron.gold_data_cron', '>> ~/cron.log'),
    ('0 17 * * *', 'goldapp.cron.gold_data_cron', '>> ~/cron.log')
]
CRONTAB_COMMAND_SUFFIX = '2>&1'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (uploads and such)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '../debug.log',
        },
    },
}

# # Configure image pipeline
# Temporary local directory to store images
IMAGES_STORE = STATIC_URL + 'tempImages/'
