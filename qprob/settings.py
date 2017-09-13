import logging
from os import environ, pardir
from random import shuffle, choice
from os.path import join, dirname

from raven import fetch_git_sha
from dotenv import load_dotenv

BASE_DIR = dirname(dirname(__file__))
load_dotenv(join(BASE_DIR, '.env'))

DEV_ENV  = int(environ.get("DEV_ENV"))

SITE_ID = 1
EXISTING_SITE = int(environ.get("EXISTING_SITE"))
SITE_NAME = environ.get("SITE_NAME")
SHORT_SITE_NAME = environ.get("SHORT_SITE_NAME")
SITE_FOLDER = environ.get("SITE_FOLDER")
if DEV_ENV:
    BASE_URL = environ.get("DEV_BASE_URL")
else:
    BASE_URL = environ.get("BASE_URL")
DOMAIN = BASE_URL
HOST = environ.get("HOST")
IP = environ.get("IP")
KEYWORD = environ.get("KEYWORD")
SITE_THEME = environ.get("SITE_THEME")
FEED_DESCRIPTION = 'Latest (5 days) of news on {}.'.format(SITE_THEME)
RESEARCH_MODULE = int(environ.get("RESEARCH_MODULE"))
DEFINITIONS_MODULE = int(environ.get("DEFINITIONS_MODULE"))
TWITTER_HANDLE = environ.get("TWITTER_HANDLE")
FACEBOOK_HANDLE = environ.get("FACEBOOK_HANDLE")
LINKEDIN_HANDLE = environ.get("LINKEDIN_HANDLE")
GOOGLE_PLUS_HANDLE = environ.get("GOOGLE_PLUS_HANDLE")
LOGO_HANDLE = environ.get("LOGO_HANDLE")
FEEDBURNER_URI = environ.get("FEEDBURNER_URI")
# if you remove this copy, please include some other link to my site
COPYRIGHT = 'Developed by <a href="https://talaikis.com">Quantrade Ltd.</a> &copy;, 2017 | v. 2.0'
SHOW_BOOKS_ON_THEME = int(environ.get("SHOW_BOOKS_ON_THEME"))
CACHE_ENABLED = int(environ.get("CACHE_ENABLED"))
DELAY_REQUESTS = int(environ.get("DELAY_REQUESTS"))
GET_YOUTUBE = int(environ.get("GET_YOUTUBE"))
GET_AMAZON = int(environ.get("GET_AMAZON"))
POST_TO_TWITTER = int(environ.get("POST_TO_TWITTER"))
POST_TO_FACEBOOK = int(environ.get("POST_TO_FACEBOOK"))
SEARCH_TITLE = environ.get("SEARCH_TITLE")
FIRST_PAGE_TITLE = environ.get("FIRST_PAGE_TITLE")
ALLOWED_HOSTS = [HOST, "localhost", "127.0.0.1", IP]
TEMPLATE_NAME = environ.get("TEMPLATE_NAME")
PAGE_ID = environ.get("PAGE_ID")
ACCESS_TOKEN = environ.get("ACCESS_TOKEN")
HOOK_SECRET = environ.get("HOOK_SECRET")
QPROB_PROJECTS = environ.get("QPROB_PROJECTS").split(", ")
MOBILE_APP_URL = environ.get("MOBILE_APP_URL")

ELASTIC_IP = environ.get("ELASTIC_IP")
LIMIT_POSTS = int(environ.get("LIMIT_POSTS"))
TWITTER_PER_PAGE = int(environ.get("TWITTER_PER_PAGE"))
POSTS_PER_PAGE = int(environ.get("POSTS_PER_PAGE"))
DEFINITIONS_PER_PAGE = int(environ.get("DEFINITIONS_PER_PAGE"))
VIDEOS_PER_PAGE = int(environ.get("VIDEOS_PER_PAGE"))
BOOKS_PER_PAGE = int(environ.get("BOOKS_PER_PAGE"))

CONSUMER_KEY = environ.get("CONSUMER_KEY")
CONSUMER_SECRET =environ.get("CONSUMER_SECRET")
ACCESS_TOKEN_KEY = environ.get("ACCESS_TOKEN_KEY")
ACCESS_TOKEN_SECRET = environ.get("ACCESS_TOKEN_SECRET")

AMAZON_ACCESS_KEY = environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOC_TAG = environ.get("AMAZON_ASSOC_TAG")

DEVELOPER_KEY = environ.get("DEVELOPER_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

SECRET_KEY = environ.get("SECRET_KEY")

#=========================================================================================
#                 NOT SPECIFIC TO SITE
#=========================================================================================

SHOW_DEBUG = int(environ.get("SHOW_DEBUG"))

if DEV_ENV:
    DATABASE_USER = environ.get("DEV_DATABASE_USER")
    DATABASE_PASSWORD = environ.get("DEV_DATABASE_PASSWORD")
    DATABASE_NAME = '{}'.format(environ.get("DEV_DATABASE_NAME"))
else:
    DATABASE_USER = environ.get("DATABASE_USER")
    DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD")
    DATABASE_NAME = '{}'.format(environ.get("DATABASE_NAME"))

DEV_PORT = environ.get("DEV_PORT")

if DEV_ENV:
    DATABASE_HOST = environ.get("DEV_DB_HOST")
else:
    DATABASE_HOST = environ.get("DB_HOST")
DATABASE_PORT = int(environ.get("DATABASE_PORT"))

if DEV_ENV:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

ROOT_URLCONF = 'qprob.urls'

ADMINS = (
    ('', ''),
)

MANAGERS = ADMINS

AD_CODE = """
    <!-- Instead of article image responsive -->
    <ins class="adsbygoogle"
    style="display:block"
    data-ad-client="ca-pub-2578395398126606"
    data-ad-slot="2747813439"
    data-ad-format="auto"></ins>
    <script>
    (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
"""

INSTALLED_APPS = [
    #'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'aggregator',
    'haystack',
    'raven.contrib.django.raven_compat',
]

STATICFILES_DIRS = []

MEDIA_ROOT = join(BASE_DIR, "uploads")
STATIC_ROOT = join(BASE_DIR, "static")
STATIC_URL = "/static/"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

if (not DEV_ENV) | CACHE_ENABLED:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '{}:11211'.format(IP),
            #LOCATION': [
                #'12.19.26.20:11211',
                #'12.19.26.22:11211',
            #]
            #'LOCATION': 'unix:/tmp/memcached.sock',
            'TIMEOUT': 86400, #12 hours
            #'OPTIONS': {
                #'MAX_ENTRIES': 20000
            #}
        }
    }

    CACHE_MIDDLEWARE_KEY_PREFIX = 'csh_{}'.format(SITE_FOLDER)
    CACHE_MIDDLEWARE_SECONDS = 21600

RAVEN_CONFIG = {
    'dsn': environ.get("RAVEN_DSN"),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    #'release': fetch_git_sha(dirname(pardir)),
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8',
        },
    }
}

DEBUG = DEV_ENV

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://{}:9200/'.format(ELASTIC_IP),
        'INDEX_NAME': '{}_idx'.format(SITE_FOLDER),
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'

DEFAULT_FROM_EMAIL = environ.get("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_HOST = environ.get("EMAIL_HOST")
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 2525
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_NOREPLY = environ.get("EMAIL_NOREPLY")
#EMAIL_SSL_KEYFILE = ''
#EMAIL_SSL_CERTFILE = ''
NOTIFICATIONS_EMAILS = [environ.get("NOTIFICATIONS_EMAILS")]
NOTIFICATIONS_ENABLED = True

#SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'collector.social_profile.SendVerificationEmail'
#SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email_verify_sent/'

def load_user_agents(uafile=join(BASE_DIR, 'user_agents.txt')):
    uas = []
    with open(uafile, 'r') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    shuffle(uas)
    return uas


HEADERS = {
    "Connection" : "close",
    'User-Agent': choice(load_user_agents()),
    'referer': BASE_URL,
}

PROXIES_LIST = ['97.77.104.22:80']

SSL_PROXIES = ['97.77.104.22:80']

PROXIES = {
    'http': '',#random.choice(PROXIES_LIST),
    'https': ''#random.choice(SSL_PROXIES),
}

TIMEOUT = 240

USE_L10N = True
USE_I18N = True
LANGUAGE_CODE = 'en-us'
DEFAULT_CHARSET = 'UTF-8'


USE_TZ = False
TIME_ZONE = 'UTC'
DATETIME_FORMAT = 'N j, Y, HH'
SHORT_DATETIME_FORMAT = 'Y-m-d'
DATE_FORMAT = 'N j, Y'

DEBUG_FILE = join(BASE_DIR, "logs", "django.log")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': DEBUG_FILE,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if (not DEV_ENV) | CACHE_ENABLED:
    MIDDLEWARE += [
        'django.middleware.cache.UpdateCacheMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
    ]

MIDDLEWARE += [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]

if DEV_ENV:
    DEBUG_CONTEXT = ['django.template.context_processors.debug']
else:
    DEBUG_CONTEXT = []

TEMPL_DIRS = ['templates',]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPL_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':  DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'aggregator.context_processors.extra_context',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ] + DEBUG_CONTEXT,
        },
    },
]

# QProb specific settings
MINIMUM_PARAGRAPH = 10
MINIMUM_SENTENCE = 10
MINIMUM_IMAGE = 250
SUMMARIZER_SENTENCES = 2
MINIMUM_TITLE = 5

WSGI_APPLICATION = 'qprob.wsgi.application'
