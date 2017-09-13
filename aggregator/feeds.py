from datetime import time, datetime, timedelta
from mimetypes import MimeTypes
from os import stat

from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.html import strip_tags
from django.conf import settings

from .models import Post


class LatestArticlesFeed(Feed):
    title = settings.SITE_NAME
    link = settings.BASE_URL
    if settings.DEV_ENV:
        folder = "{0}\\".format(settings.BASE_DIR)
    else:
        folder = settings.BASE_DIR + '/'
    description = settings.FEED_DESCRIPTION

    def items(self):
        return Post.objects.filter(date__gte=(datetime.now() - timedelta(days=3))).order_by('date').reverse()[:50]

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return datetime.combine(item.date, time())

    def item_category(self, item):
        return item.category

    def item_link(self, item):
        return "{0}{1}/".format(settings.BASE_URL, item.slug)

    def item_description(self, item):
        text = item.summary or ""
        return strip_tags(text)

    def item_enclosure_url(self, item):
        try:
            image = "{0}{1}".format(self.link, item.image)
            return image
        except:
            return None


    def item_enclosure_length(self, item):
        try:
            size = stat("{0}{1}".format(self.folder, item.image)).st_size
            return size
        except:
            return None

    def item_enclosure_mime_type(self, item):
        mime = MimeTypes()
        try:
            mime_type = mime.guess_type("{0}{1}".format(self.folder, item.image))[0]
            return mime_type
        except:
            return None

    def item_author_name(self, item):
        return item.category

    def item_author_link(self, item):
        return item.category
