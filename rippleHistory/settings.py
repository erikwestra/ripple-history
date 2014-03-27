""" rippleHistory.settings

    This module defines the global settings for the "rippleHistory" system.
"""
import os.path
import sys

import dj_database_url

from rippleHistory.shared.lib.settingsImporter import SettingsImporter

#############################################################################

# Calculate the absolute path to the top-level directory for this project.

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#############################################################################

# Load our various custom settings.

import_setting = SettingsImporter(globals(),
                                  custom_settings="rippleHistory.custom_settings",
                                  env_prefix="RH_")

import_setting("DEBUG",                     True)
import_setting("SET_ALLOWED_HOSTS",         True)
import_setting("TIME_ZONE",                 "UTC")
import_setting("DATABASE_URL",              None)
# NOTE: DATABASE_URL uses the following general format:
#           postgres://username:password@host:port/database_name
#       or for a database on the local machine:
#           postgres://username:password@localhost/database_name
import_setting("LOG_DIR",                   os.path.join(ROOT_DIR, "logs"))
import_setting("ENABLE_DEBUG_LOGGING",      False)
import_setting("LOGGING_DESTINATION",       "file")

#############################################################################

# Our various project settings:

if SET_ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".3taps.com", ".3taps.net"]
else:
    ALLOWED_HOSTS = ["*"]

TEMPLATE_DEBUG = DEBUG

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*a_43r7%5t*j#(#36jk50z$61gemub9clk7n9ifkho$g92@f55'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Enable the "south" database migration toolkit.

    "south",

    # Our rippleHistory applications

    "rippleHistory.shared",
    "rippleHistory.api",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rippleHistory.urls'

WSGI_APPLICATION = 'rippleHistory.wsgi.application'

STATIC_URL = '/static/'

# Set up our database.

if 'test' in sys.argv:
    # Use SQLite for unit tests.
    DATABASES = {'default' : {'ENGINE' : "django.db.backends.sqlite3"}}
else:
    # Use dj_database_url to extract the database settings from the
    # DATABASE_URL setting.
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Set up our logging.  We log everything to the console for now.

LOGGING = {
    'version' : 1,

    'disable_existing_loggers' : True,

    'formatters' : {
#        'verbose' : {
#            'format' : "%(levelname)s %(asctime)s %(module)s %(message)s",
#        },
        'simple' : {
            'format' : "%(levelname)s %(message)s",
        },
    },

    'handlers' : {
        'console' : {
            'level'     : "DEBUG",
            'class'     : "logging.StreamHandler",
            'formatter' : "simple",
        },
#        'file' : {
#            'level'     : "DEBUG",
#            'class'     : "logging.FileHandler",
#            'filename'  : "/path/to/file.log",
#            'formatter' : "simple",
#        },
        'null' : {
            'level' : "DEBUG",
            'class' : "django.utils.log.NullHandler",
        },
    },

    'loggers' : {
        '' : {
            'handlers' : ["console"],
            'level'     : "DEBUG",
            'propagate' : False,
        },

        'django.db.backends' : {
            'handlers'  : ["null"], # Disable query logging when DEBUG=True.
            'level'     : "DEBUG",
            'propagate' : False,
        },
    }
}

