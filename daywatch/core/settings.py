# -*- coding: utf-8 -*-

import os

### Server Settings

ADMINS = (
    ('Raul Garreta', 'raul@tryolabs.com'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

SECRET_KEY = '!8anh!ke*m+u6wq*d$cdroi=$tw$!een6(t7#k!%zr!buy@)^q'

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

HOST_NAME_CHOICES = (
    ('localhost', 'localhost'),
)

### Static Files

MEDIA_URL = ''

STATIC_URL = '/static/'

SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = os.path.join(SETTINGS_DIR, '..', '..', 'media/')
STATIC_ROOT = os.path.join(SETTINGS_DIR, '..', '..', 'static/')

# Sass files should be compiled with django-libsass
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

### Template Settings

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = ()

### Middleware Settings

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

### App Settings

# import djcelery
# djcelery.setup_loader()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    # Third party packages
    'south',
    'rosetta',
    'captcha',
    'djcelery',
    'widget_tweaks',
    'gunicorn',
    'compressor',
    'bootstrap_pagination',
    # Core
    'core',
    # API
    'rest_framework',
    'api',
    # GUI
    'gui',
    'gui.analytics_panel',
    'gui.spiders_panel',
    'gui.items_panel',
    'gui.trends_panel',
)

### Email settings

SERVER_EMAIL = 'info@usedaywatch.com'
DEFAULT_FROM_EMAIL = 'info@usedaywatch.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'user@domain.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_SUBJECT_PREFIX = '[Daywatch] '
EMAIL_SENDER = "[django-chronograph]"

### Localization and Internationalization Settings

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('en', 'English'),
    ('es', 'Spanish'),
    ('pt', 'Portuguese'),
)

ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = 'es'
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = 'Spanish'
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
BING_APP_ID = '...'
ROSETTA_EXCLUDED_APPLICATIONS = ('chronograph',)

### Authentication Settings

AUTH_PROFILE_MODULE = 'core.UserProfile'

LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Captcha - google.com/recaptcha
RECAPTCHA_PUBLIC_KEY = '6Lej78ISAAAAAIRhfZZMJgwJMJcQZXi8rXvGIj6f'
RECAPTCHA_PRIVATE_KEY = '6Lej78ISAAAAAIIZuSXd9M0ZeYodvrQePBDigfeY'

# Delete logs older than N hours
ERROR_LOG_CLEAN = 3

### Time Settings

TIME_ZONE = 'UTC'

###  Local Settings

try:
    from local_settings import *
except:
    pass

### Celery Settings

BROKER_URL = 'redis://localhost:6379/0'
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_IMPORTS = ['core.tasks']

### DjangoRestFramework Settings

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

### South Settings

SOUTH_TESTS_MIGRATE = False

### Custom Variables

# The date format used throughout the application, so we don't constantly have
# to check the reference.
DW_DATE_FORMAT = '%Y-%m-%d'
