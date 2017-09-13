from django.conf import settings
from django.db.models import Count

from .models import (Category, Post)


def extra_context(request):
    cats = Category.objects.all()

    c = []
    for cat in cats:
        cats_ = {}
        cats_['cnt'] = Post.objects.filter(category=cat.title).count()
        cats_['title'] = cat.title
        cats_['slug'] = cat.slug
        if cats_['cnt'] > 0:
            c.append(cats_)

    archive = []
    years = Post.objects.dates('date', 'year')
    for year in years:
        archive.append({'year': year.year, 'cnt': Post.objects.filter(date__year=year.year).count()})

    return {'base_url': settings.BASE_URL[:-1],
            'sitename': settings.SITE_NAME,
            'cats': c,
            'keyword': settings.KEYWORD,
            'shot_site_name': settings.SHORT_SITE_NAME,
            'research_module': settings.RESEARCH_MODULE,
            'definitions_module': settings.DEFINITIONS_MODULE,
            'twitter_handle': settings.TWITTER_HANDLE,
            'facebook_handle': settings.FACEBOOK_HANDLE,
            'linkedin_handle': settings.LINKEDIN_HANDLE,
            'gplus_handle': settings.GOOGLE_PLUS_HANDLE,
            'logo_handle': settings.LOGO_HANDLE,
            'feedburner_uri': settings.FEEDBURNER_URI,
            'copyright': settings.COPYRIGHT,
            'search_title': settings.SEARCH_TITLE,
            'site_theme': settings.SITE_THEME,
            'first_page_title': settings.FIRST_PAGE_TITLE,
            'advert': settings.AD_CODE,
            'host': settings.HOST,
            'folder': settings.SITE_FOLDER,
            'years': archive,
            'mobile_app_url': settings.MOBILE_APP_URL,
            'app_name': 'aggregator' }
