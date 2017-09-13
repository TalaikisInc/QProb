import asyncio
from os import name

if not name is 'nt':
    import uvloop

from django.core.management.base import BaseCommand

from aggregator.tasks import parse_all_feeds, title_cleaner_from_db,\
    update_db_with_cleaned_content, feed_status_checker, banner


class Command(BaseCommand):
    help = 'Parses feeds and exewcutes additional cleaning.'

    def handle(self, *args, **options):
        if not name is 'nt':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()

        feed_status_checker(loop=loop)
        parse_all_feeds(loop=loop)
        banner()
        title_cleaner_from_db(loop=loop)
        update_db_with_cleaned_content(loop=loop)

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
