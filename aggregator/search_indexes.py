from haystack import indexes

from .models import (Post, Twits, Video)
from django.utils.html import strip_tags
from django.conf import settings

if settings.RESEARCH_MODULE:
    from .models import ScienceArticle


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    rendered = indexes.CharField(use_template=True, indexed=False)

    title = indexes.CharField(model_attr='title')
    summary = indexes.CharField(model_attr='summary')
    content = indexes.CharField(model_attr='content')
    #date = indexes.DateTimeField(model_attr='date')
    url = indexes.CharField(model_attr='url')
    category = indexes.CharField(model_attr='category__title')
    feed_content = indexes.CharField(model_attr='feed_content')


    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


if settings.RESEARCH_MODULE:
    class ScienceArticleIndex(indexes.SearchIndex, indexes.Indexable):
        text = indexes.CharField(document=True, use_template=True)
        #rendered = indexes.CharField(use_template=True, indexed=False)

        title = indexes.CharField(model_attr='title')
        summary = indexes.CharField(model_attr='summary')
        content = indexes.CharField(model_attr='text')
        #date = indexes.DateTimeField(model_attr='date')
        url = indexes.CharField(model_attr='slug')
        category = indexes.CharField(model_attr='category__title')

        def get_model(self):
            return ScienceArticle

        def index_queryset(self, using=None):
            return self.get_model().objects.all()
