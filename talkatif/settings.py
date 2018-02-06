"""
Django settings for talkatif project.

Generated by 'django-admin startproject' using Django 1.10.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)


from decouple import config, Csv

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'haystack',
    'debate.apps.DebateConfig',
    'discourse.apps.DiscourseConfig',
    'anymail',
    'mptt',
    'markdownx',
    'zinnia', #blog
    'tagging',
    'versatileimagefield',
    'django_user_agents',

    #used by chron to send emails
    'django.contrib.sites',
    'chroniker',
    'compressor',

    'markdownify',

    #used by newsletter
    'django_extensions',
    'sorl.thumbnail',
    'newsletter',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:

    #social signin plugins
    'allauth.socialaccount.providers.facebook',
    #'allauth.socialaccount.providers.linkedin',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.google',

    'taggit',
    'widget_tweaks',
    'el_pagination',
    'django_social_share',


    'meta', #adds metadata to sites
    'imagekit',
    'robots', #Generates site.xml file for crawlers
    'django_comments_xtd',
    'django_comments',
    'django_markdown2',
    'rest_framework',
    'django_countries',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'talkatif.urls'

SITE_ID = 4

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                #'zinnia.context_processors.version', optional
                'django.template.context_processors.media',
                'debate.context_processors.site_processor',

            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    #django object permissions
    'guardian.backends.ObjectPermissionBackend',
)

WSGI_APPLICATION = 'talkatif.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}



# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
#STATICFILES_DIRS = [    os.path.join(BASE_DIR, "static"),]

COMPRESS_ROOT =  os.path.join(BASE_DIR, "static")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SERVER_EMAIL = config('EMAIL') #configured email for sending notifications

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "POSTMARK_SERVER_TOKEN": config('POSTMARK_TOKEN'),
}
EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"  # or sendgrid.EmailBackend, or...
DEFAULT_FROM_EMAIL = config('EMAIL')  # if you don't already have this in settings

#Authentication Setting
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = '/all/'
LOGOUT_REDIRECT_URL = '/index/'
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED=True
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_PRESERVE_USERNAME_CASING =False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Required by django-allauth to extend the sign up form to include profile data
ACCOUNT_FORMS = {'signup': 'debate.forms.SignupForm'}

#Django-meta settings
META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = "talkatif.com"
META_DEFAULT_KEYWORDS = ["debate","faceoff","talk", "opinions", "criticism", "rebuttal", "argument", "discourse", "discussion", "polls", "poll"]
META_USE_SITES = True


STATICFILES_FINDERS = (
'django.contrib.staticfiles.finders.FileSystemFinder',
'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

TAGGIT_CASE_INSENSITIVE = True #taggit settings

#Django-chrontab settings

# CRONJOBS = [
#     ('*/1 * * * *', 'myapp.cron.my_scheduled_job')
# ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'comparison': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'comparison',
        'TIMEOUT': None,
   }
}


#comment manager
MANAGERS = (
    ('Ogun Sewade', config('EMAIL') ),
)

#To allow comment flagging, likes and dislikes
COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'debate.postdebate': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    },

    'discourse.post': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    }
}


#COMMENTS_XTD Settings
COMMENTS_APP = 'django_comments_xtd'
COMMENTS_XTD_API_USER_REPR = lambda u: u.get_full_name()

#Comment Threading settings
COMMENTS_XTD_MAX_THREAD_LEVEL = 10  # default is 0
COMMENTS_XTD_LIST_ORDER = ('thread_id', 'order')  # default is ('thread_id', 'order')

#Disable comments confirmation for new users
COMMENTS_XTD_CONFIRM_MAIL = False

#  To help obfuscating comments before they are sent for confirmation.
COMMENTS_XTD_SALT = (b"Timendi causa est nescire. "
                     b"Aequam memento rebus in arduis servare mentem.")

# Source mail address used for notifications.
COMMENTS_XTD_FROM_EMAIL = "noreply@example.com"

# Contact mail address to show in messages.
COMMENTS_XTD_CONTACT_EMAIL = "helpdesk@example.com"

SERIALIZATION_MODULES = {
    'xml':    'tagulous.serializers.xml_serializer',
    'json':   'tagulous.serializers.json',
    'python': 'tagulous.serializers.python',
    'yaml':   'tagulous.serializers.pyyaml',
}

#pure pagination settings
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,

    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}

#django-el-pagination settings
#used to paginate comments
EL_PAGINATION_PER_PAGE = 20

#django newsletter settings
# Amount of seconds to wait between each email. Here 100ms is used.
NEWSLETTER_EMAIL_DELAY = 0.1

# Amount of seconds to wait between each batch. Here one minute is used.
NEWSLETTER_BATCH_DELAY = 60

# Number of emails in one batch
NEWSLETTER_BATCH_SIZE = 100

#versatile image field settings
VERSATILEIMAGEFIELD_SETTINGS = {
    'create_images_on_demand': True,
    }
VERSATILEIMAGEFIELD_USE_PLACEHOLDIT = True

#MAthjax
MATHJAX_ENABLED=True


#Markdown Settings

from datetime import datetime
MARKDOWNX_URLS_PATH = '/attachment/markdownify/'
MARKDOWNX_UPLOAD_URLS_PATH = '/attachment/upload/'
MARKDOWNX_MEDIA_PATH = datetime.now().strftime('attachment/%Y/%m/%d/')
MARKDOWNX_UPLOAD_MAX_SIZE = 4 * 1024 * 1024 #4 MB in bytes
MARKDOWNX_IMAGE_MAX_SIZE = {
    'size': (300, 0),
    'quality': 80
}
