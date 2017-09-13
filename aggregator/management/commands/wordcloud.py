from django.core.management.base import BaseCommand

from aggregator.tasks import full_wordcloud, posts_wordcloud


class Command(BaseCommand):
    help = 'Parses feeds and exewcutes additional cleaning.'

    def handle(self, *args, **options):
        full_wordcloud()
        posts_wordcloud()

        self.stdout.write(self.style.SUCCESS('Successfully generated wordclouds.'))