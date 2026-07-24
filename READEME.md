# 🔍 Django & Elasticsearch Local Setup & Troubleshooting Guide

This document contains the complete guide for running Elasticsearch locally with Django (`django-elasticsearch-dsl`), including setup steps, required configurations, code samples, and troubleshooting for common errors like `ConnectionTimeout` and `503 search_phase_execution_exception`.

---

## 🛠️ Diagnostics & Root Causes

During local development, Elasticsearch operations often fail or hang (`ConnectionTimeout`) for three main reasons:

1. **Disk Watermark Lockouts (`status: red`):** By default, Elasticsearch locks writes and shard allocations if your disk usage passes 85–90%.
2. **Unassigned Replica Shards:** Elasticsearch defaults to expecting multiple nodes for index replicas. On a single local node, this causes `index.create()` to stall waiting for a second node.
3. **Short Client Timeout:** The Python driver defaults to a 30-second timeout, which isn't long enough when the cluster is initializing or under high CPU load.

---

## 📋 Required Project Configurations

### 1. Document Configuration (`documents.py`)

Set `'number_of_replicas': 0` so Elasticsearch does not wait for a second node during index creation:

```python
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Item


@registry.register_document
class ItemDocument(Document):
    class Index:
        name = 'items'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,  # CRITICAL for single-node local setup
        }

    class Django:
        model = Item
        fields = [
            'title',
            'description',
        ]
```

### 2. Django Settings Configuration (`settings.py`)

Increase the driver timeout and enable auto-retry:

```python
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://localhost:9200',
        'timeout': 60,  # Increased from 30s
        'max_retries': 3,
        'retry_on_timeout': True,
    },
}
```

### 3. Safe View Handling (`views.py`)

Catch potential Elasticsearch API errors gracefully so your Django site doesn't crash:

```python
from django.shortcuts import render
from .documents import ItemDocument
from elasticsearch.exceptions import ApiError


def home(request):
    query = request.GET.get('search_query', '').strip()
    results = []

    if query:
        try:
            search = ItemDocument.search().query(
                "multi_match", query=query, fields=['title', 'description']
            )
            results = search.execute()
        except ApiError as e:
            print(f"Elasticsearch execution error: {e}")
            results = []

    return render(request, 'index.html', {'results': results, 'query': query})
```

---

## 🚀 Step-by-Step Environment Startup

### Step 1: Start Elasticsearch Container

Run the Docker container with bounded memory (512m) and disabled disk watermark checks:

```bash
sudo docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e "cluster.routing.allocation.disk.threshold_enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

### Step 2: Verify Cluster Health

Wait ~10 seconds and test the endpoint:

```bash
curl -i http://localhost:9200/_cluster/health
```

**Expected Output:** HTTP 200 with `"status": "green"` or `"status": "yellow"`. Do not proceed if status is `"red"`.

### Step 3: Index Data and Run Django

```bash
# 1. Activate Virtual Environment
source .venv/bin/activate

# 2. Run Database Migrations
python manage.py migrate

# 3. Rebuild Search Index
python manage.py search_index --rebuild -f

# 4. Start Development Server
python manage.py runserver
```

---

## 🔧 Useful Recovery Commands

**Disable disk thresholds on a running cluster:**

```bash
curl -X PUT "http://localhost:9200/_cluster/settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "persistent": {
      "cluster.routing.allocation.disk.threshold_enabled": false
    }
  }'
```

**Clean Docker system resources:**

```bash
sudo docker system prune -a --volumes
```

**Wipe and reset the container:**

```bash
sudo docker stop elasticsearch && sudo docker rm elasticsearch
```

---

## 📑 Quick Diagnostic Reference Table

| Symptom / Error | Primary Cause | Resolution |
|---|---|---|
| `elastic_transport.ConnectionTimeout` | Disk full or unassigned replica shards (Status: red). | Disable disk threshold and set `'number_of_replicas': 0`. |
| `503 search_phase_execution_exception` | Corrupted index schema or red cluster state. | Rebuild index with `python manage.py search_index --rebuild -f`. |
| `Cannot connect to the Docker daemon` | Docker permission issue or daemon stopped. | Use `sudo docker` or start Docker Desktop. |