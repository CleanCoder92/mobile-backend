# https://docs.djangoproject.com/en/1.10/ref/settings/

import os

from decouple import config  # noqa


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)


SITE_ID = 1

SECURE_HSTS_PRELOAD = True

DEBUG = True

ADMINS = (("Admin", "foo@example.com"),)

AUTH_USER_MODEL = "users.User"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_js_reverse",
    "django_ses",
    'rest_framework',
    'rest_framework.authtoken',
    "webpack_loader",
    "import_export",
    "rest_auth",
    'django.contrib.sites',
    'rest_auth.registration',
    'django_tables2',
    "fcm_django",
    "corsheaders",

    "api",
    "common",
    "users",
    "cubes",
    "tiles",
    "share",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

]

FCM_DJANGO_SETTINGS = {
        "APP_VERBOSE_NAME": "Clout 9",
        "FCM_SERVER_KEY": "AAAAyRvKctM:APA91bFnbM8ZC5yxLu7bYthedgs5oqerYrQjgKMu_w0bX6VEoL2msfxqC1LvS-H-OT9st79XVm0Iugl6RTiaungnzx5URQL_Qbn-oI5_k96MYKfhgPjSPgGiWEFowFUZHfRdK4g0kGQk",
        "ONE_DEVICE_PER_USER": True,
        "DELETE_INACTIVE_DEVICES": True,
}

ROOT_URLCONF = "Clout9.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [base_dir_join("templates")],
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

WSGI_APPLICATION = "Clout9.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = (base_dir_join("./templates/assets"),)

# Webpack
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": False,  # on DEBUG should be False
        "STATS_FILE": base_dir_join("../webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [".+\.hot-update.js", ".+\.map"],
    }
}

# Celery
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE
CORS_ORIGIN_ALLOW_ALL = True
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Sentry
SENTRY_DSN = config("SENTRY_DSN", default="")
COMMIT_SHA = config("HEROKU_SLUG_COMMIT", default="")

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'api.serializers.LoginSerializer'
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default="")
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default="")
