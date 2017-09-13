import asyncio

import uvloop

from django.core.management.base import BaseCommand

from aggregator.tasks import (content_if_empty_all, update_db_with_cleaned_content,
    empty_sources)


class Command(BaseCommand):
    help = 'Rechecks empty content.'

    def handle(self, *args, **options):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)

        content_if_empty_all(loop=loop)
        update_db_with_cleaned_content(loop=loop)
        empty_sources(loop=loop)

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
