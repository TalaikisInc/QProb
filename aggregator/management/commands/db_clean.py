from django.core.management.base import BaseCommand

from aggregator.tasks import db_cleaner


class Command(BaseCommand):
    help = 'Drops invisible data.'

    def handle(self, *args, **options):
        db_cleaner()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
