import asyncio

import uvloop

from django.core.management.base import BaseCommand
from aggregator.amazon import (parse_by_categories, parse_by_keywords)


class Command(BaseCommand):
    help = 'Parses Amazon.'

    def handle(self, *args, **options):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)

        parse_by_categories(loop=loop)
        #TODO keywords should be fixed, as it has hard coded kws
        parse_by_keywords(loop=loop)

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done jobs'))
