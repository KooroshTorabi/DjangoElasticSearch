# ➕ Adding Items to the Django & Elasticsearch Project

This guide explains how to add new `Item` records to your Django app. Since the project uses `django-elasticsearch-dsl`, any item you create in Django is automatically synced to Elasticsearch through signals — no manual indexing required, as long as the app is set up correctly.

---

## 1. Django Admin (Easiest for Testing)

Register the `Item` model in `admin.py`:

```python
from django.contrib import admin
from .models import Item

admin.site.register(Item)
```

Then create a superuser (if you haven't already) and log in to the admin panel:

```bash
python manage.py createsuperuser
python manage.py runserver
```

Navigate to:

```
http://localhost:8000/admin/
```

You can now add, edit, and delete `Item` records through the UI.

---

## 2. Django Shell

Useful for quickly adding test data:

```bash
python manage.py shell
```

```python
from myapp.models import Item

Item.objects.create(title="Sample Item", description="This is a test item.")
```

Replace `myapp` with the actual name of your Django app.

---

## 3. Django View + Form

To let users add items through your website, create a `ModelForm`:

```python
# forms.py
from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description']
```

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ItemForm

def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ItemForm()
    return render(request, 'add_item.html', {'form': form})
```

```html
<!-- templates/add_item.html -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Add Item</button>
</form>
```

Add a URL route:

```python
# urls.py
from django.urls import path
from .views import add_item

urlpatterns = [
    path('add-item/', add_item, name='add_item'),
]
```

---

## 4. Confirm the Item Was Indexed in Elasticsearch

Query the index directly to verify:

```bash
curl http://localhost:9200/items/_search?pretty
```

You should see your newly created item in the `hits` array.

---

## 5. Troubleshooting: Item Not Appearing in Elasticsearch

If items created in Django aren't showing up in search results, it usually means the signal handlers that sync Django → Elasticsearch aren't registered, or the index is out of sync. Force a full rebuild:

```bash
python manage.py search_index --rebuild -f
```

If that resolves it but new items still don't sync automatically going forward, double-check that:

- `django_elasticsearch_dsl` is listed in `INSTALLED_APPS`
- `ItemDocument` is correctly registered with `@registry.register_document`
- The Elasticsearch container is running and healthy (`curl http://localhost:9200/_cluster/health`)