"""
Django settings for tapir project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "fl%20e9dbkh4mosi5$i$!5&+f^ic5=7^92hrchl89x+)k0ctsn"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bootstrap4",
    "tapir.accounts",
    "tapir.shifts",
    "tapir.utils",
    "tapir.coop",
    "tapir.finance",
    "tapir.odoo",
    # TODO(Leon Handreke): Don't install in prod
    "django_extensions",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tapir.accounts.middleware.StaffCheckMiddleware",
]

ROOT_URLCONF = "tapir.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["tapir/templates/"],
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

WSGI_APPLICATION = "tapir.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "ldap": {
        "ENGINE": "ldapdb.backends.ldap",
        "NAME": "ldap://openldap/",
        "USER": "cn=admin,dc=supercoop,dc=de",
        "PASSWORD": "admin",
    },
}
DATABASE_ROUTERS = ["ldapdb.router.Router"]

ODOO = {
    "BASE_URL": "http://odoo:8069/",
    # Used because in development, the web interface is accessed from the Docker host
    "WEB_BASE_URL": "http://127.0.0.1:8069/",
    "DATABASE": "odoo",
    "USERNAME": "admin",
    "PASSWORD": "admin",
}

ODOO_TAX_ID_NOT_TAXABLE = 20
ODOO_JOURNAL_ID_CASH = 6
ODOO_JOURNAL_ID_BANK = 7

# SKR03 8200 "Erlöse"
ODOO_ACCOUNT_ID_8200 = 1151
# SKR03 0810 "Geschäftsguthaben der verbleibenden Mitglieder"
ODOO_ACCOUNT_ID_0810 = 161


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "tapir" / "static",
]

WEASYPRINT_BASEURL = "/"

REG_PERSON_BASE_DN = "ou=people,dc=supercoop,dc=de"
REG_PERSON_OBJECT_CLASSES = ["inetOrgPerson", "organizationalPerson", "person"]
REG_GROUP_BASE_DN = "ou=groups,dc=supercoop,dc=de"
REG_GROUP_OBJECT_CLASSES = ["groupOfNames"]

# Groups are stored in the LDAP tree
GROUP_VORSTAND = "vorstand"
# This is our own little stupid permission system. See explanation in accounts/models.py.
PERMISSIONS = {
    "shifts.manage": [GROUP_VORSTAND],
    "coop.manage": [GROUP_VORSTAND],
    "accounts.manage": [GROUP_VORSTAND],
}


AUTH_USER_MODEL = "accounts.TapirUser"
LOGIN_REDIRECT_URL = "accounts:user_me"
