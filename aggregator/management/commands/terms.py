from django.core.management.base import BaseCommand, CommandError
from aggregator.term_collector import (parse, make_summaries, remove_unwanted)

class Command(BaseCommand):
    help = 'Terms parser.'

    def handle(self, *args, **options):
        #TODO make normal commands for each function
        #parse()
        #make_summaries()
        remove_unwanted()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
