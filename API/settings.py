"""
Django settings for API project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import yaml


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# DB_FILE = os.path.join(BASE_DIR, 'Database_config.txt')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v)b-$e@83=f@%b73%s_^tgg^mh!tgvad(9yug9x@_!ta_j!&84'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ADMIN_ENABLED = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tastypie',
    'API'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'API.urls'

WSGI_APPLICATION = 'API.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

#USE BELOW TO DEBUG ON LOCAL MACHINE
#dirc = os.path.dirname(__file__)
#db_path = os.path.join(dirc, 'database_config.example.yml')
#db_file = open(db_path, 'r')
#DATABASES = yaml.load(db_file)

dirc = os.path.dirname(__file__)
db_path = os.path.join(dirc, 'database.yml')
db_file = open(db_path, 'r')
DATABASE = yaml.load(db_file)
DATABASE = DATABASE['production']
DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql',
                         'NAME': DATABASE['database'],
                         'USER': DATABASE['username'],
                         'PASSWORD': DATABASE['password'],
                         'HOST': DATABASE['host'],
                         'PORT': DATABASE['port']}}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
