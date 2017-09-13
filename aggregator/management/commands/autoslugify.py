from django.core.management.base import BaseCommand, CommandError
from aggregator.models import Books

class Command(BaseCommand):
    help = 'Autoslugifies table. No longer used after autosluggifier.'

    def handle(self, *args, **options):
        books = Books.objects.all()

        for book in books:
            book.title = book.title
            book.save()

        self.stdout.write(self.style.SUCCESS('Successfully done jobs'))
