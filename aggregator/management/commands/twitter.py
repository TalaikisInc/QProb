import asyncio

import uvloop

from django.core.management.base import BaseCommand, CommandError

from aggregator.tasks import (tweets_to_db, tweets_by_tag_to_db, clean_tweet_hashtags)


class Command(BaseCommand):
    help = 'Twitter parser.'

    def handle(self, *args, **options):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)

        tweets_to_db(loop=loop)
        tweets_by_tag_to_db(loop=loop)
        clean_tweet_hashtags(loop=loop)

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
