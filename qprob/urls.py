from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import (handler400, handler403, handler404, handler500)
from django.views.decorators.cache import never_cache

from aggregator.views import (ArticleDetailView, ArticleListView, FeedbackCreate,
    SourceCreate, VideoListView, TwitsListView, BookListView, BookDetailView,
    sentiment_view, today_view, book_categories_view, PostYearArchiveView,
    api_main, auto_deploy, tag_stats)
from aggregator.feeds import LatestArticlesFeed
if settings.DEFINITIONS_MODULE:
    from aggregator.views import (terms_dictionary, TermListView)
if settings.RESEARCH_MODULE:
    from aggregator.views import (ScienceListView, science_categories_view)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', ArticleListView.as_view(), name='post_list'),
    url(r'^(?P<slug>[-\w]+)/$', ArticleDetailView.as_view(), name='post_detail'),
    url(r'^book/(?P<slug>[-\w]+)/$', BookDetailView.as_view(), name='book_detail'),
    url(r'^page/(?P<page>[0-9]+)/$', ArticleListView.as_view(), name='post_list'),

    url(r'^tag/(?P<tag_slug>[-\w]+)/$', ArticleListView.as_view(), name='post_list_by_tag'),
    url(r'^source/(?P<cat_slug>[-\w]+)/$', ArticleListView.as_view(), name='post_list_by_tag'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', ArticleListView.as_view(), name='post_list_by_tag'),
    url(r'^source/(?P<cat_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', ArticleListView.as_view(), name='post_list_by_tag'),

    url(r'^videos/(?P<vid_slug>[-\w]+)/$', VideoListView.as_view(), name='video_list_by_channel'),
    url(r'^videos/(?P<vid_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', VideoListView.as_view(), name='video_list_by_channel'),

    url(r'^tweets/(?P<twit_slug>[-\w]+)/$', TwitsListView.as_view()),
    url(r'^tweets/(?P<twit_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', TwitsListView.as_view()),

    url(r'^books/(?P<book_slug>[-\w]+)/$', BookListView.as_view()),
    url(r'^books/(?P<book_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', BookListView.as_view()),

    #date views
     url(r'^news/(?P<year>[0-9]{4})/$', PostYearArchiveView.as_view()),
     url(r'^news/(?P<year>[0-9]{4})/page/(?P<page>[0-9]+)/$', PostYearArchiveView.as_view()),

    url(r'^{}/feed/$'.format(settings.KEYWORD), LatestArticlesFeed()),
    url(r'^{}/books/$'.format(settings.KEYWORD), book_categories_view, name='book_cats'),
    url(r'^{}/feedback/$'.format(settings.KEYWORD), never_cache(FeedbackCreate.as_view()), name='feedback_form'),
    url(r'^{}/add/$'.format(settings.KEYWORD), never_cache(SourceCreate.as_view()), name='source_form'),
    url(r'^{}/sentiment/$'.format(settings.KEYWORD), sentiment_view, name="sentiments"),
    url(r'^{}/today/$'.format(settings.KEYWORD), today_view, name="today"),
    url(r'^{}/search/'.format(settings.KEYWORD), include('haystack.urls')),
    url(r'^{}/api/$'.format(settings.KEYWORD), api_main, name='api_main'),
    url(r'^{}/tag_stats/$'.format(settings.KEYWORD), tag_stats, name='tag_stats'),

    url(r'^api/auto_deploy/$', auto_deploy, name='auto_deploy'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEFINITIONS_MODULE:
    urlpatterns += [url(r'^{}/definitions/$'.format(settings.KEYWORD), terms_dictionary, name='terms_dictionary'),
        url(r'^define/(?P<term_slug>[-\w]+)/$', TermListView.as_view()),
        url(r'^define/(?P<term_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', TermListView.as_view()),]

if settings.RESEARCH_MODULE:
    urlpatterns += [url(r'^{}/research/$'.format(settings.KEYWORD), science_categories_view, name='science_cats'),
        url(r'^research/(?P<sci_slug>[-\w]+)/$', ScienceListView.as_view()),
        url(r'^research/(?P<sci_slug>[-\w]+)/page/(?P<page>[0-9]+)/$', ScienceListView.as_view()),]

handler400 = 'aggregator.views.bad_request'
handler403 = 'aggregator.views.permission_denied'
handler404 = 'aggregator.views.page_not_found'
handler500 = 'aggregator.views.server_error'
