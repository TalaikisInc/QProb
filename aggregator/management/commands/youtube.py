import asyncio

import uvloop

from django.core.management.base import BaseCommand
from aggregator.youtube import do_youtube, clean_youtube_text


class Command(BaseCommand):
    help = 'Youtube searcher for article titles.'

    def handle(self, *args, **options):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)

        do_youtube(loop=loop)
        clean_youtube_text(loop=loop)

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done Youtube jobs'))
