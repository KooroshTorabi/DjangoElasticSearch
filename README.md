# 🔍 Django & Elasticsearch Search Project

A Django application integrated with Elasticsearch for fast, full-text search, using [`django-elasticsearch-dsl`](https://django-elasticsearch-dsl.readthedocs.io/). It includes a local Docker-based Elasticsearch setup, models and views for adding and searching items, a management command to seed the database with random fake data, and full setup/troubleshooting documentation.

---

## ✨ Features

- Full-text search over `Item` records using Elasticsearch
- Automatic syncing between Django models and the Elasticsearch index via `django-elasticsearch-dsl` signals
- Local single-node Elasticsearch setup via Docker
- Admin, shell, and form-based workflows for adding items
- Management command to seed the database with random fake items (`Faker`)
- Documented troubleshooting for common local dev issues (`ConnectionTimeout`, disk watermark lockouts, unassigned shards)

---

## 📦 Requirements

- Python 3.10+
- Django
- `django-elasticsearch-dsl`
- Docker
- `Faker` (optional, for fake data seeding)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Elasticsearch (Docker)

```bash
sudo docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e "cluster.routing.allocation.disk.threshold_enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

Verify it's running:

```bash
curl -i http://localhost:9200/_cluster/health
```

Expected: HTTP 200 with `"status": "green"` or `"status": "yellow"`.

### 4. Run migrations and build the search index

```bash
python manage.py migrate
python manage.py search_index --rebuild -f
```

### 5. Start the development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000`.

---

## 📁 Project Structure (relevant files)

```
myapp/
├── documents.py                        # Elasticsearch document mapping (ItemDocument)
├── forms.py                            # ItemForm for adding items
├── models.py                           # Item model
├── views.py                            # Search view + add_item view
├── templates/
│   └── add_item.html                   # Form template for adding items
└── management/
    └── commands/
        └── seed_items.py               # Command to seed 50+ fake items
```

---

## ➕ Adding Items

You can add `Item` records via:

- **Django Admin** — `http://localhost:8000/admin/`
- **Django Shell** — `Item.objects.create(title="...", description="...")`
- **The web form** — `http://localhost:8000/add-item/`

Full details in **[ADDITEM.md](./ADDITEM.md)**.

---

## 🌱 Seeding Fake Data

Populate the database with random fake items for testing:

```bash
python manage.py seed_items            # adds 50 items (default)
python manage.py seed_items --count 100
python manage.py seed_items --flush
```

Full details in **[SEEDITEMS.md](./SEEDITEMS.md)**.

---

## 🔎 Searching

Search is exposed through the `home` view, which queries `ItemDocument` across `title` and `description` fields using a `multi_match` query, and gracefully handles Elasticsearch API errors.

---

## 🛠️ Troubleshooting

Common local Elasticsearch issues (`ConnectionTimeout`, `503 search_phase_execution_exception`, disk watermark lockouts, unassigned replica shards) along with diagnostics and fixes are documented below.

| Symptom / Error | Primary Cause | Resolution |
|---|---|---|
| `elastic_transport.ConnectionTimeout` | Disk full or unassigned replica shards (Status: red). | Disable disk threshold and set `'number_of_replicas': 0`. |
| `503 search_phase_execution_exception` | Corrupted index schema or red cluster state. | Rebuild index with `python manage.py search_index --rebuild -f`. |
| `Cannot connect to the Docker daemon` | Docker permission issue or daemon stopped. | Use `sudo docker` or start Docker Desktop. |

---

## 📄 Additional Documentation

- [`ADDITEM.md`](./ADDITEM.md) — How to add items (admin, shell, form)
- [`SEEDITEMS.md`](./SEEDITEMS.md) — How to seed random fake items

---

## 🏷️ Topics

`django` `elasticsearch` `django-elasticsearch-dsl` `python` `docker` `full-text-search`

---

## 📜 License

Add your license of choice here (e.g. MIT, Apache 2.0).