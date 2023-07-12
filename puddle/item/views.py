from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import NewItemForm, EditItemForm


def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    related_items = Item.objects.filter(category=item.category, is_solve=False).exclude(pk=pk)[0:3]

    context = {
        'item': item,
        'related_items': related_items
    }
    return render(request, 'item/detail.html', context)


def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    items = Item.objects.filter(is_solve=False)
    if category_id:
        items = items.filter(category_id=category_id)

    if query:
        items = items.filter(Q(name__icontains=query) | Q(descriptions__icontains=query))
    context = {
        'query': query,
        'items': items,
        'title': 'search',
        'categories': categories,
        'category_id': int(category_id)
    }
    return render(request, 'item/items.html', context)


@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('item:detail', pk=item.id)
    else:
        form = NewItemForm()
    context = {
        'form': form,
        'title': 'New Item',
    }
    return render(request, 'item/form.html', context)


@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)
    context = {
        'form': form,
        'title': 'Edit Item',
    }
    return render(request, 'item/form.html', context)


@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    item.delete()

    return redirect('dashboard:index')
