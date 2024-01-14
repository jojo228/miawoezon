import os
from typing import Any, Dict
from pathlib import Path
from django.conf.global_settings import LANGUAGES as DJANGO_LANGUAGES
from django.core.management.utils import get_random_secret_key
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = os.getenv('DEBUG', 'False') == 'False'

if not DEBUG:
    DEBUG_PROPAGATE_EXCEPTIONS = True

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(',')
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'False') == 'True'



# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = ["django_countries", "django_seed", "storages"]


PROJECT_APPS = [
    "announcement.apps.AnnouncementConfig",
    "blog.apps.BlogConfig",
    "staff_account.apps.StaffAccountConfig",
    "main.apps.MainConfig",
    "authentication.apps.AuthenticationConfig",
    "rooms.apps.RoomsConfig",
    "reservations.apps.ReservationsConfig",
    "lists.apps.ListsConfig",
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.locale.LocaleMiddleware",

]

ROOT_URLCONF = 'miawoezon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'miawoezon.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


if DEBUG:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
            'default': {
                'ENGINE': os.getenv('DB_ENGINE'),
                'NAME': os.getenv('DB_NAME'),
                'USER': os.getenv('DB_USER'),
                'PASSWORD': os.getenv('DB_PASSWORD'),
                'HOST': os.getenv('DB_HOST'),
                'PORT': os.getenv('DB_PORT'),
            }
    }

#Session timeout config

SESSION_EXPIRE_SECONDS = 3600  # 1 hour

SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

SESSION_TIMEOUT_REDIRECT = 'authentication:login'


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles/")

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP Configuration (Its working fine, just add the mail and its password)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL")

PASSWORD_RESET_TIMEOUT = 14400


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "authentication.backends.MyBackend",
]

# Auth

LOGIN_URL = "/authentication/login/"


# Locale
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)


# if not DEBUG:

#     # AWS S3 collectstatic

#     DEFAULT_FILE_STORAGE = "config.custom_storages.UploadStorage"
#     STATICFILES_STORAGE = "config.custom_storages.StaticStorage"
#     AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
#     AWS_STORAGE_BUCKET_NAME = "airbnb-clone-ssayebee"
#     AWS_AUTO_CREATE_BUCKET = True
#     AWS_BUCKET_ACL = "public_read"
#     AWS_S3_REGION_NAME = "ap-northeast-2"
#     AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
#     AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
#     STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

#     # Sentry

#     sentry_sdk.init(
#         dsn=os.environ.get("SENTRY_URL"),
#         integrations=[DjangoIntegration()],
#         send_default_pii=True,
#     )
