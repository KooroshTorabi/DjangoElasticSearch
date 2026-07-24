"""
Django management command to seed the database with random fake Items.

INSTALLATION:
    1. Install Faker:
         pip install Faker

    2. Place this file at:
         ElasticSearch/management/commands/seed_items.py

       (Django requires the management/commands folder structure. Create
       empty __init__.py files in both 'management/' and 'management/commands/'
       if they don't already exist.)

    3. Replace 'ElasticSearch' below with the actual name of your Django app.

USAGE:
    python manage.py seed_items              # adds 50 items (default)
    python manage.py seed_items --count 100   # adds a custom number of items
    python manage.py seed_items --flush       # deletes existing items first, then seeds
"""

from django.core.management.base import BaseCommand
from faker import Faker

from ElasticSearch.models import Item  # <-- update 'ElasticSearch' to your actual app name

fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with random fake Item records."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of fake items to create (default: 50)',
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing Item records before seeding.',
        )

    def handle(self, *args, **options):
        count = options['count']
        flush = options['flush']

        if flush:
            deleted, _ = Item.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing item(s)."))

        items = [
            Item(
                title=fake.sentence(nb_words=4).rstrip('.'),
                description=fake.paragraph(nb_sentences=3),
            )
            for _ in range(count)
        ]

        Item.objects.bulk_create(items)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} fake item(s)."))
        self.stdout.write(
            self.style.NOTICE(
                "Run 'python manage.py search_index --rebuild -f' if the items "
                "don't appear in Elasticsearch automatically."
            )
        )