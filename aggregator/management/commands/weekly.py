import asyncio
from os import name

if not name is 'nt':
    import uvloop

from django.core.management.base import BaseCommand

from aggregator.tasks import url_status_checker, feed_status_checker, \
    clean_images_from_db, clean_images_from_folder, img_resizer, \
    make_category_thumbs


class Command(BaseCommand):
    help = 'Weekly QProb tasks.'

    def handle(self, *args, **options):
        if not name is 'nt':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()

        url_status_checker(loop=loop)
        feed_status_checker(loop=loop)
        clean_images_from_db(loop=loop)
        clean_images_from_folder(loop=loop)
        img_resizer(loop=loop)

        loop.close()

        make_category_thumbs()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
