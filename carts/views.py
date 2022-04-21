from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import CartItem, Cart
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

# This is private function. by adding underscore
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)     # get the product
    # Getting Product Varaition
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value) # __iexact will ignore if the key is capital later or small later.
                product_variation.append(variation)
            except:
                pass

    # Getting Cart
    try:
        cart = Cart.objects.get(cart_id =_cart_id(request)) # get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    # Getting Cart Item

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists() # Chechk cart item exists or not (Bolean)
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart) # This will return cart item objects
        # Checking Variations inside the existing variation, So we can increase the quantity of cart item
        # Existing Variations -> Database
        # Current Variation -> product_variation
        # Item_id -> Database
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id) # I will start from here
        print(ex_var_list)

        if product_variation in ex_var_list:
            # Increase the cart item quantity (to do this we need cart item id)
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()

        else:
            # Creat a new cart item
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation) 
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )

        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass    
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items: # To Show cart items details
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        # global tax
        tax = 2 * total / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass #just ignore

    context = { # Make Context dictionary to pass values to the cart template
        'total': total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }

    return render(request, 'store/cart.html', context)