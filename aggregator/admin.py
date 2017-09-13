from django.contrib import admin
from django.conf import settings

from aggregator.models import (Post, Category, Tags, Sources, Twits, \
    Feedback, TwitsByTag, Video, Books, BooksCat)

if settings.RESEARCH_MODULE:
    from aggregator.models import (ScienceArticle, ScienceCat)

if settings.DEFINITIONS_MODULE:
    from aggregator.models import  (Terms, TermLinks)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'sentiment', 'image')
    list_filter = ('pub_date', 'category')
    search_fields = ('title', 'working_content')
    #list_select_related = ('category', 'feed')
    date_hierarchy = 'date'

class SourcesAdmin(admin.ModelAdmin):
    list_display = ('feed', 'twitter_handle', 'name', 'email', 'active', 'dead', 'failures')
    list_filter = ('active', 'name')
    search_fields = ('feed', 'twitter_handle')

class TagsAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')
    list_filter = ('active', 'tag_type')
    search_fields = ('title', 'tag_type')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'thumbnail')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')
    search_fields = ('name', 'email')

class TwitsAdmin(admin.ModelAdmin):
    list_display = ('content', 'date', 'twitter_handle', 'hashtags')
    list_filter = ('date', 'screen_name')
    search_fields = ('content', 'hashtags', 'twitter_handle__feed')

class TwitsByTagAdmin(admin.ModelAdmin):
    list_display = ('content', 'date', 'twitter_handle', 'hashtags')
    list_filter = ('date', 'by_tag')
    search_fields = ('content', 'hashtags', 'twitter_handle__feed')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel_title', 'slug', 'description')
    search_fields = ('title', 'description', 'slug')

class BooksCatAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', 'slug')

class BooksAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'slug')
    search_fields = ('title', 'review')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Twits, TwitsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Sources, SourcesAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(TwitsByTag, TwitsByTagAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(BooksCat, BooksCatAdmin)
admin.site.register(Books, BooksAdmin)

#------------------------------------------------------------------------------
# MODULAR
#------------------------------------------------------------------------------

if settings.DEFINITIONS_MODULE:
    class TermsAdmin(admin.ModelAdmin):
        list_display = ('term', 'text', 'image', 'movies')
        search_fields = ('term', 'text')

    class TermLinksAdmin(admin.ModelAdmin):
        list_display = ('link', 'status_parsed')
        list_filter = ('status_parsed', 'link')
        #search_fields = ('link', 'hashtags', 'twitter_handle__feed')

    admin.site.register(Terms, TermsAdmin)
    admin.site.register(TermLinks, TermLinksAdmin)


if settings.RESEARCH_MODULE:
    class ScienceArticleAdmin(admin.ModelAdmin):
        list_display = ('title', 'file', 'pdf_url')
        search_fields = ('title', 'text', 'pdf_url')

    class ScienceCatAdmin(admin.ModelAdmin):
        list_display = ('title', 'slug')
        search_fields = ('title', 'slug')

    admin.site.register(ScienceArticle, ScienceArticleAdmin)
    admin.site.register(ScienceCat, ScienceCatAdmin)
