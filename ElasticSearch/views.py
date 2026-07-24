from django.shortcuts import render, redirect
from .documents import ItemDocument
from .forms import ItemForm


def home(request):
    query = request.GET.get('search_query', '')
    results = []

    if query:
        # Match search_query against both 'title' and 'description' fields
        search = ItemDocument.search().query("multi_match", query=query, fields=['title', 'description'])
        results = search.execute()

    return render(request, 'index.html', {'results': results, 'query': query})


# def home(request):
#     user_input = ""
#     if request.method == "POST":
#         # Get the value submitted in the text box
#         user_input = request.POST.get("search_query", "")
#         # You can add logic here later (e.g., query Elasticsearch)
#
#     return render(request, "index.html", {"user_input": user_input})

def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ItemForm()
    return render(request, 'add_item.html', {'form': form})