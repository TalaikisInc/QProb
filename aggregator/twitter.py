import datetime

from clint.textui import colored
import twitter

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from aggregator.models import Post


# TODO this client isn't asynced, but probably not important for the purpoise of the project
api = twitter.Api(consumer_key=settings.CONSUMER_KEY,
    consumer_secret=settings.CONSUMER_SECRET,
    access_token_key=settings.ACCESS_TOKEN_KEY,
    access_token_secret=settings.ACCESS_TOKEN_SECRET)


async def get_tweets(handle):
    try:
        tweets = api.GetUserTimeline(screen_name=handle, exclude_replies=True,
            include_rts=False)  # includes entities
        return tweets
    except:
        return None


async def twitter_date(value):
    split_date = value.split()
    del split_date[0], split_date[-2]
    value = ' '.join(split_date)  # Fri Nov 07 17:57:59 +0000 2014 is the format
    return datetime.datetime.strptime(value, '%b %d %H:%M:%S %Y')


async def get_tweets_by_tag(tag):
    try:
        tweets = api.GetSearch(term=tag, raw_query=None, geocode=None, since_id=None,
            max_id=None, until=None, since=None, count=50, lang='en', locale=None,
            result_type="mixed", include_entities=True)
        return tweets
    except:
        return None


async def get_tags(post):
    try:
        if post.tags.all().count() > 0:
            tags_ = "".join(["#{0} ".format(tag) for tag in post.tags])[:20]
        else:
            tags_ = None
    except Exception as e:
        print(colored.red("At twitter get_tags {}".format(e)))
        tags_ = None

    return tags_


async def get_media(post):
    if post.image:
        media = "{0}{1}".format(settings.DOMAIN, post.image)
    else:
        media = None

    return media


async def post_tweet(data):
    try:
        post = Post.objects.get(title=data['title'])

        tags = await get_tags(post=post)
        media = await get_media(post=post)
        sentiment = post.sentiment or "N/A"

        if not (tags is None):
            status = "{0} [{1}]: {2}{3}/ {4}".format(post.title[:80], sentiment, settings.DOMAIN, post.slug, tags)
        else:
            status = "{0} [{1}]: {2}{3}/".format(post.title[:80], sentiment, settings.DOMAIN, post.slug)

        if not (media is None):
            api.PostUpdate(status=status, media=media)
        else:
            api.PostUpdate(status=status, media=None)

        print(colored.green("Sent tweet {}.".format(status)))

    except Exception as e:
        print(colored.red("At Twitter post: {0}".format(e)))
