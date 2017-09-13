import asyncio
from os import name

if not name is 'nt':
    import uvloop
from nltk import pos_tag
from nltk.tokenize import word_tokenize

from django.core.management.base import BaseCommand
from django.utils.html import strip_tags

from aggregator.models import Tags, Post
from aggregator.tasks import save_tags
from aggregator.text_tools import words_wo_stopwords, WordCloudMod, filter_insignificant


async def processs_content(post):
    text = words_wo_stopwords(strip_tags(post.content))
    #TODO this is duplicated job, should be improved
    words = word_tokenize(strip_tags(text))
    taggged = pos_tag(words)
    cleaned = filter_insignificant(taggged)
    text = " ".join(cleaned)
    wc = WordCloudMod().generate(text)
    result = list(wc.keys())[:10]
    
    if len(result) > 0:
        post = await save_tags(tags=result, entry=post)
        post.save()


class Command(BaseCommand):
    help = 'Extracts keywords from posts content and saves to posts.'

    def handle(self, *args, **options):
        if not name is 'nt':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()

        posts = Post.objects.all()
        loop.run_until_complete(asyncio.gather(*[processs_content(post=post) \
            for post in posts], return_exceptions=True))

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully extracted keywords for posts'))

