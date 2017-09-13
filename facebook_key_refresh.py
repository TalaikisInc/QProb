from os import environ

import requests
from dotenv import load_dotenv

load_dotenv('.env')
FB_CLIENT_ID = environ.get("FB_CLIENT_ID")
FB_CLIENT_SECRET = environ.get("FB_CLIENT_SECRET")
PAGE_ACCESS_TOKEN = environ.get("PAGE_ACCESS_TOKEN")
SITE_FOLDER = environ.get("SITE_FOLDER")


def main():
    print(SITE_FOLDER)
    r = requests.get('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={0}&client_secret={1}&fb_exchange_token={2}'.format(FB_CLIENT_ID, FB_CLIENT_SECRET, PAGE_ACCESS_TOKEN))
    print(r.text.split('"')[3])


main()