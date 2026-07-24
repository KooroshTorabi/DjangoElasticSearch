# 🌱 Seeding Random Fake Items

This guide explains how to populate your `Item` model with random fake data using a custom Django management command and the `Faker` library. This is useful for local testing, demos, and verifying that Elasticsearch indexing works correctly with a larger dataset.

---

## 1. Install Faker

```bash
pip install Faker
```

---

## 2. Add the Management Command

Django management commands must live in a specific folder structure inside your app:

```
myapp/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── seed_items.py
```

Create the empty `__init__.py` files if they don't already exist:

```bash
mkdir -p myapp/management/commands
touch myapp/management/__init__.py
touch myapp/management/commands/__init__.py
```

Then place the `seed_items.py` command file inside `myapp/management/commands/`.

> ⚠️ Inside `seed_items.py`, update the import line to match your actual app name:
> ```python
> from myapp.models import Item
> ```

---

## 3. The Command

```python
from django.core.management.base import BaseCommand
from faker import Faker

from myapp.models import Item  # <-- update 'myapp' to your actual app name

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
```

---

## 4. Usage

**Add 50 fake items (default):**

```bash
python manage.py seed_items
```

**Add a custom number of items:**

```bash
python manage.py seed_items --count 100
```

**Wipe existing items first, then seed:**

```bash
python manage.py seed_items --flush
```

---

## 5. Sync with Elasticsearch

`bulk_create()` bypasses Django's normal `save()` signals, which `django-elasticsearch-dsl` relies on for automatic syncing. If your new fake items don't show up in search results, rebuild the index manually:

```bash
python manage.py search_index --rebuild -f
```

---

## 6. Verify

Check the database:

```bash
python manage.py shell
```
```python
from myapp.models import Item
Item.objects.count()
```

Check Elasticsearch:

```bash
curl http://localhost:9200/items/_search?pretty
```