import asyncio
import dateutil.parser

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from nltk.tokenize import sent_tokenize
from clint.textui import colored

from django.db import IntegrityError
from django.conf import settings

from .models import Video, Post


# TODO requires better channel management, as probably most of content isn't even used
# have videos by post title, need all videos for page?, not just channel


async def save_video(entry, post):
    try:
        video = Video.objects.create(title=entry['title'],
            description=entry['description'], date=entry['date'],
            channel_title=entry['channel_title'],
            channel_id=entry['channel_id'], video_id=entry['video_id'])
        video.save()
        #TODO filter out duplicate errors

        post.videos.add(entry['title'])
        post.save()
    except IntegrityError:
        pass
    except Exception as e:
        print("[ERROR] At save video: {0}".format(e))


async def youtube_date(value):
    dte_ = dateutil.parser.parse(value)
    dte = dte_.replace(tzinfo=None)

    return dte


async def clean_video(video):
    text = []
    try:
        if len(video.description) > 0:
            sentence_tokens = sent_tokenize(video.description)

            for sentence in sentence_tokens:
                if not ('http' in sentence):
                    text.append("{0} ".format(sentence))

        video.description = "".join("{} ".format(s) for s in text)
        video.save()
        if settings.SHOW_DEBUG:
            print(colored.green("Cleaned video description saved to db: {0}".format(video.title)))
    except Exception as e:
        print(colored.red("At clean_video {}".format(e)))


def clean_youtube_text(loop):
    videos = Video.objects.all()

    loop.run_until_complete(asyncio.gather(*[clean_video(video=video) \
        for video in videos], return_exceptions=True
    ))


async def youtube_search(q, max_results):
    youtube = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, developerKey=settings.DEVELOPER_KEY)
    search_response = youtube.search().list(q=q, part="id,snippet", maxResults=max_results).execute()

    videos = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            video = {}

            video['title'] = search_result["snippet"]['title']
            video['description'] = search_result["snippet"]['description']
            video['date'] = await youtube_date(search_result["snippet"]['publishedAt'])
            video['channel_title'] = search_result["snippet"]['channelTitle']
            video['channel_id'] = search_result["snippet"]['channelId']
            video['video_id'] = search_result["id"]["videoId"]
            videos.append(video)

    return videos


async def do_youtube_once(post, loop):
    res = await youtube_search(q=post.title, max_results=25)

    if len(res) > 0:
        asyncio.gather(*[save_video(entry=entry, post=post) for entry in res],
            return_exceptions=True
        )


async def make_videos(post, loop):
    res = await youtube_search(q=post.title, max_results=25)

    if len(res) > 0:
        asyncio.gather(*[save_video(entry=entry, post=post) for entry in res],
            return_exceptions=True
        )


def do_youtube(loop):
    posts = Post.objects.all()

    loop.run_until_complete(asyncio.gather(*[make_videos(\
        post=post, loop=loop) for post in posts], \
        return_exceptions=True
    ))
