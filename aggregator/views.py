import datetime
import hmac
from hashlib import sha1
from subprocess import call
from ipaddress import ip_network
from functools import lru_cache

import requests
from ipware.ip import get_real_ip

from django.db.models import Count
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.utils.text import slugify
from django.views.generic.dates import YearArchiveView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse_lazy
from django.db.models import Avg
from django.utils.encoding import force_bytes

from .models import Post, Tags, Sources, Category, Feedback, Twits, TwitsByTag,\
    Video, Books, BooksCat
if settings.RESEARCH_MODULE:
    from .models import ScienceArticle
if settings.DEFINITIONS_MODULE:
    from .models import Terms


#TODO year/ month archives
#TODO refactor


def api_main(request):
    api_host = "api.{}".format(settings.HOST)
    return render(request, '{}/api.html'.format(settings.TEMPLATE_NAME), {'api_domain': api_host })


class PostYearArchiveView(YearArchiveView):
    queryset = Post.objects.all()
    paginate_by = settings.POSTS_PER_PAGE
    allow_empty = True
    date_field = "date"
    make_object_list = True
    allow_future = True


if settings.RESEARCH_MODULE:
    class ScienceListView(ListView):

        model = ScienceArticle
        paginate_by = settings.POSTS_PER_PAGE

        def get_queryset(self):

            query_set = super(ScienceListView, self).get_queryset()

            main_qs = query_set.order_by('date').reverse()

            if self.kwargs:
                try:
                    self.sci_slug = self.kwargs['sci_slug']
                except:
                    return main_qs

                try:
                    qs = query_set.filter(category__slug=self.sci_slug).order_by('date').reverse()
                    return qs
                except:
                    return main_qs

            return main_qs


        def get_context_data(self, **kwargs):
            context = super(ScienceListView, self).get_context_data(**kwargs)

            science_lists = self.get_queryset()

            paginator = Paginator(science_lists, self.paginate_by)
            try:
                page = self.kwargs['page']
            except:
                page = 1

            try:
                scienceart = paginator.page(page)
            except PageNotAnInteger:
                scienceart = paginator.page(1)
            except EmptyPage:
                scienceart = paginator.page(paginator.num_pages)

            context['scienceart'] = scienceart
            context['sci'] = self.kwargs['sci_slug']

            return context


if settings.DEFINITIONS_MODULE:
    class TermListView(ListView):

        model = Terms
        paginate_by = settings.DEFINITIONS_PER_PAGE

        def get_queryset(self):

            query_set = super(TermListView, self).get_queryset()

            main_qs = query_set

            if self.kwargs:
                try:
                    self.term_slug = self.kwargs['term_slug']
                except:
                    return main_qs

                try:
                    qs = query_set.filter(term__startswith=self.term_slug).title()
                    return qs
                except:
                    return main_qs

            return main_qs


        def get_context_data(self, **kwargs):
            context = super(TermListView, self).get_context_data(**kwargs)

            term_lists = self.get_queryset()

            paginator = Paginator(term_lists, self.paginate_by)
            try:
                page = self.kwargs['page']
            except:
                page = 1

            try:
                terms = paginator.page(page)
            except PageNotAnInteger:
                terms = paginator.page(1)
            except EmptyPage:
                terms = paginator.page(paginator.num_pages)

            context['terms'] = terms
            context['term_slug'] = self.kwargs['term_slug']

            return context


class BookListView(ListView):
    model = Books
    paginate_by = settings.BOOKS_PER_PAGE

    def get_queryset(self):
        query_set = super(BookListView, self).get_queryset()

        main_qs = query_set.filter(categories__enabled=settings.SHOW_BOOKS_ON_THEME)

        if self.kwargs:
            try:
                self.cat = self.kwargs['book_slug']
            except:
                try:
                    self.cat = self.kwargs['book_slug']
                except:
                    return main_qs

            try:
                cat = BooksCat.objects.get(slug=self.cat)
                return query_set.filter(categories__in=[cat]).order_by("publication_date").reverse()
            except:
                return main_qs

        return main_qs


    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)

        #paginator implementation
        book_lists = Books.objects.order_by("publication_date").reverse()#.defer("working_content", "feed_content", "feed", "pub_date", "content", 'videos')

        paginator = Paginator(book_lists, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)

        context['books'] = books
        context['assoc_tag'] = settings.AMAZON_ASSOC_TAG

        try:
            context['book_slug'] = self.kwargs['book_slug']
            context['book_category'] = BooksCat.objects.get(slug=self.kwargs['book_slug']).title
        except:
            return context

        return context


class VideoListView(ListView):

    model = Video
    paginate_by = settings.VIDEOS_PER_PAGE

    def get_queryset(self):

        query_set = super(VideoListView, self).get_queryset()

        main_qs = query_set.order_by('date').reverse()

        if self.kwargs:
            try:
                self.vid_slug = self.kwargs['vid_slug']
            except:
                return main_qs

            try:
                qs = query_set.filter(slug=self.vid_slug).order_by('date').reverse()
                return qs
            except:
                return main_qs

        return main_qs


    def get_context_data(self, **kwargs):
        context = super(VideoListView, self).get_context_data(**kwargs)

        video_lists = self.get_queryset()

        paginator = Paginator(video_lists, self.paginate_by)
        try:
            page = self.kwargs['page']
        except:
            page = 1

        try:
            videos = paginator.page(page)
        except PageNotAnInteger:
            videos = paginator.page(1)
        except EmptyPage:
            videos = paginator.page(paginator.num_pages)

        context['videos'] = videos
        context['vid'] = self.kwargs['vid_slug']

        return context


class TwitsListView(ListView):
    model = Twits
    paginate_by = settings.TWITTER_PER_PAGE

    def get_queryset(self):

        query_set = super(TwitsListView, self).get_queryset()

        main_qs = query_set.order_by('date').reverse()

        if self.kwargs:
            try:
                self.twit_slug = self.kwargs['twit_slug']
            except:
                return main_qs

            try:
                qs = query_set.order_by('date').reverse().filter(twitter_handle__twitter_handle=self.twit_slug)
                return qs
            except:
                return main_qs

        return main_qs

    def get_context_data(self, **kwargs):
        context = super(TwitsListView, self).get_context_data(**kwargs)

        twit_lists = self.get_queryset()

        paginator = Paginator(twit_lists, self.paginate_by)
        try:
            page = self.kwargs['page']
        except:
            page = 1

        try:
            twits = paginator.page(page)
        except PageNotAnInteger:
            twits = paginator.page(1)
        except EmptyPage:
            twits = paginator.page(paginator.num_pages)

        context['twits'] = twits
        context['twit_slug'] = self.kwargs['twit_slug']

        return context


class ArticleListView(ListView):
    model = Post
    paginate_by = settings.POSTS_PER_PAGE
    def get_queryset(self):
        query_set = super(ArticleListView, self).get_queryset()
        main_qs = query_set.order_by('date').reverse()[:settings.LIMIT_POSTS]
        if self.kwargs:
            try:
                self.tag = self.kwargs['tag_slug']
            except:
                try:
                    self.cat = self.kwargs['cat_slug']
                except:
                    return main_qs
            try:
                tag = Tags.objects.get(slug=self.tag)
                return query_set.filter(tags__in=[tag]).order_by('date').reverse()
            except:
                try:
                    cat = Category.objects.get(slug=self.cat)
                    return query_set.filter(category__in=[cat]).order_by('date').reverse()
                except:
                    return main_qs
            else:
                raise Http404
        return main_qs

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        posts_lists = Post.objects.defer("working_content", "feed_content", "feed", "pub_date", "content", 'videos')
        paginator = Paginator(posts_lists, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        try:
            context['cat'] = self.kwargs['cat_slug']
        except:
            try:
                context['tag'] = self.kwargs['tag_slug']
            except:
                return context

        return context


if settings.RESEARCH_MODULE:
    def science_categories_view(request):
        from .models import ScienceCat

        cats = ScienceCat.objects.all()
        return render(request, '{}/science_cats.html'.format(settings.TEMPLATE_NAME), {'science_cats': cats})


if settings.DEFINITIONS_MODULE:
    def terms_dictionary(request):
        from .models import Terms
        from .text_tools import replace_all_nonasy

        replacements = {'/': '', '%': '', ' ': '', "\"": '', '.': '', '-': ''}

        terms = Terms.objects.all().values('term')

        lst = []
        for l in terms:
            term = replace_all_nonasy(l['term'][:1], replacements)
            if len(term) > 0:
                lst.append(term)

        dic = []
        total = 0
        for term in sorted(list(set(lst))):
            d = {}
            d['term'] = term
            d['cnt'] = Terms.objects.filter(term__startswith=d['term']).count()
            d['slug'] = slugify(d['term'].replace('-', '_'))
            total += d['cnt']
            dic.append(d)


        return render(request, '{}/terms_dict.html'.format(settings.TEMPLATE_NAME), {'term_dic': dic})


def book_categories_view(request):
    cats = BooksCat.objects.filter(enabled=settings.SHOW_BOOKS_ON_THEME)
    return render(request, '{}/book_cats.html'.format(settings.TEMPLATE_NAME), {'book_cats': cats})


def sentiment_view(request):
    today = datetime.datetime.now()
    period = datetime.datetime(today.year, today.month, 1) - datetime.timedelta(days=252)
    sentiments_obj = Post.objects.filter(date__gte=period)
    avg = sentiments_obj.aggregate(Avg('sentiment'))
    sentiments = [{"date": s["date"], "sentiment": (float(s["sentiment"] or 0.0) - avg["sentiment__avg"]) } for s \
        in sentiments_obj.order_by('date').values('date', 'sentiment')]

    return render(request, '{}/sentiments.html'.format(settings.TEMPLATE_NAME), {'sentiments': sentiments})


def today_view(request):
    today = datetime.datetime.now()
    period = datetime.datetime(today.year, today.month, today.day) - datetime.timedelta(days=2)
    posts = Post.objects.filter(date__gte=period).order_by('date').reverse() #.values('title', 'sentiment', 'summary', 'image', 'category', 'date', 'url', 'tags', 'slug')
    return render(request, '{}/today.html'.format(settings.TEMPLATE_NAME), {'posts': posts})


class ArticleDetailView(DetailView):

    model = Post

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)

        sentiment = context['object'].sentiment or 0.0

        if sentiment > 0:
            sentiment_color = 'bg-success'
        elif sentiment < 0:
            sentiment_color = 'bg-danger'
        else:
            sentiment_color = 'bg-warning'

        try:
            handle = context['object'].feed.twitter_handle
        except:
            handle = 'QProbcom'

        try:
            s = Sources.objects.get(twitter_handle=handle)
        except:
            s = None

        tweets = Twits.objects.filter(twitter_handle=s).order_by('date').reverse()[:10]

        if tweets.count() > 0:
            context['tweets'] = tweets
            context['twithandle'] = handle
        else:
            tweets = TwitsByTag.objects.order_by('date').reverse()[:10]
            context['twithandle'] = handle
            if tweets.count() > 0:
                context['tweets'] = tweets
            else:
                context['tweets'] = None
                context['twithandle'] = handle

        context['assoc_tag'] = settings.AMAZON_ASSOC_TAG

        return context


class BookDetailView(DetailView):
    model = Books

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)

        context['assoc_tag'] = settings.AMAZON_ASSOC_TAG

        return context


class FeedbackCreate(CreateView):
    model = Feedback
    fields = ['name', 'email', 'message']
    template_name = '{}/feedback_form.html'.format(settings.TEMPLATE_NAME)
    success_url = reverse_lazy('post_list')


class SourceCreate(CreateView):
    model = Sources
    fields = ['name', 'email', 'feed', 'twitter_handle']
    template_name = '{}/source_form.html'.format(settings.TEMPLATE_NAME)
    success_url = reverse_lazy('post_list')


def page_not_found(request):
    return render(request, template_name='{}/404.html'.format(settings.TEMPLATE_NAME), context=None, content_type=None, status=404, using=None)


def permission_denied(request):
    return render(request, template_name='{}/403.html'.format(settings.TEMPLATE_NAME), context=None, content_type=None, status=403, using=None)


def server_error(request):
    return render(request, template_name='{}/500.html'.format(settings.TEMPLATE_NAME), context=None, content_type=None, status=500, using=None)


def bad_request(request):
    return render(request, template_name='{}/400.html'.format(settings.TEMPLATE_NAME), context=None, content_type=None, status=400, using=None)


@require_POST
@csrf_exempt
def auto_deploy(request):
    branch_name = "master"
    projects = settings.QPROB_PROJECTS
    client_ip = get_real_ip(request)
    if client_ip is None:
        return HttpResponseForbidden()

    whitelist = requests.get('https://api.github.com/meta').json()['hooks']
    whitelist_ips = [valid_ip for valid_ip in ip_network(whitelist[0])]

    #FIXME
    #if not (client_ip in whitelist_ips):
        #return HttpResponseForbidden()

    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden()

    sha_name, signature = header_signature.split('=')

    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.HOOK_SECRET), msg=force_bytes(request.body), digestmod=sha1)

    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden()

    event = request.META.get('HTTP_X_GITHUB_EVENT')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        for project in projects:
            deploy_path = "/home/{}/".format(project)
            call('GIT_WORK_TREE="' + deploy_path + '" git checkout -f ' + branch_name, shell=True)

            #install all requiremrnts for all sites if changed
            call(["/bin/bash", "/home/install_reqs.sh"])
            return HttpResponse(status=200)
    return HttpResponse(status=204)


@lru_cache(maxsize=1024)
def tag_stats_maker(tags):
    res = []
    for tag in tags:
        posts_cnt = Post.objects.filter(tags__in=[tag]).count()
        if posts_cnt > 1:
            res.append({"tag": tag.title, "slug": tag.slug, "cnt": posts_cnt})
    return res


def tag_stats(request):
    tags = Tags.objects.all()
    #res = tag_stats_maker(tags=tags)
    return render(request, '{}/tag_stats.html'.format(settings.TEMPLATE_NAME), {'res': tags})
