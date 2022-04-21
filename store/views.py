from difflib import context_diff
from multiprocessing import context
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from . models import Product
from django.db.models import Q


# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available = True)
        paginator = Paginator(products, 1) # Products are the products and 6 is the number of products to be show.
        page = request.GET.get('page') # We will capture the url with page numer
        paged_products = paginator.get_page(page) # Getting page products (6) stored in above paginator variable and paste paged product in html file by passing this variable in the beow context.
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3) # Products are the products and 6 is the number of products to be show.
        page = request.GET.get('page') # We will capture the url with page numer
        paged_products = paginator.get_page(page) # Getting page products (6) stored in above paginator variable and paste paged product in html file by passing this variable in the beow context.
        product_count = products.count()

    context = {
        'products' : paged_products,
        'product_count' : product_count,
    }

    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product = single_product).exists() # Cart is the foreign key inside models of crts app, so we check cert id by accessing cart.
        # exists make it bolean

    except Exception as e:
        raise e

    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)) # __icontains wil search for this keyword inside description of the products
            product_count = products.count()
    context = {
        'products' : products,
        'product_count' : product_count,
    }

    return render(request, 'store/store.html', context)
