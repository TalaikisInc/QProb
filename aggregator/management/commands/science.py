from django.core.management.base import BaseCommand, CommandError
from aggregator.science_articles import (get_pdfs_urls, downloader, \
            parse_pdfs, make_summaries, get_abstracts)

class Command(BaseCommand):
    help = 'Parses PDFs.'

    def handle(self, *args, **options):
        #TODO make normal commands for each function
        #get_pdfs_urls()
        #downloader()
        parse_pdfs()
        #make_summaries()
        get_abstracts()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
