import sentry_sdk
from decouple import Csv, config
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa


DEBUG = False

SECRET_KEY = config("SECRET_KEY")

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT"),
    }
}

DATABASES["default"]["ATOMIC_REQUESTS"] = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

STATIC_ROOT = base_dir_join("static")
STATIC_URL = "/static/"

MEDIA_ROOT = base_dir_join("media")
MEDIA_URL = "/media/"

SERVER_EMAIL = "foo@example.com"

# EMAIL_HOST = "smtp.sendgrid.net"
# EMAIL_HOST_USER = config("SENDGRID_USERNAME")
# EMAIL_HOST_PASSWORD = config("SENDGRID_PASSWORD")
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# Security
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Webpack
WEBPACK_LOADER["DEFAULT"]["CACHE"] = True

# Celery
# CELERY_BROKER_URL = config("REDIS_URL")
# CELERY_RESULT_BACKEND = config("REDIS_URL")
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE
CORS_ORIGIN_ALLOW_ALL = True
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
AWS_ACCESS_KEY_ID = 'AKIA3DNT5UITQL2AIPGF'
AWS_SECRET_ACCESS_KEY = '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'

EMAIL_BACKEND = 'django_ses.SESBackend'


# Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE.insert(  # insert WhiteNoiseMiddleware right after SecurityMiddleware
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

# django-log-request-id
MIDDLEWARE.insert(  # insert RequestIDMiddleware on the top
    0, "log_request_id.middleware.RequestIDMiddleware"
)

LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
LOG_REQUESTS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"},
    },
    "formatters": {
        "standard": {
            "format": "%(levelname)-8s [%(asctime)s] [%(request_id)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "null": {"class": "logging.NullHandler",},
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO"},
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False,},
        "django.request": {"handlers": ["mail_admins"], "level": "ERROR", "propagate": True,},
        "log_request_id.middleware": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

JS_REVERSE_EXCLUDE_NAMESPACES = ["admin"]

# Sentry
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], release=COMMIT_SHA)
