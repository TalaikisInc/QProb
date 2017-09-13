from os import environ
from os.path import dirname, join

from django.core.wsgi import get_wsgi_application

from dotenv import load_dotenv


BASE_DIR = dirname(dirname('__file__'))
BASE_PATH = dirname(BASE_DIR)
load_dotenv(join(BASE_PATH, '.env'))

environ.setdefault("DJANGO_SETTINGS_MODULE", "qprob.settings")
application = get_wsgi_application()
