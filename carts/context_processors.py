from .models import Cart, CartItem
from .views import _cart_id


# def counter(request):
    
def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try: # Get Cart Item
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1]) # Means filter by cart id.
            # Check Numbers of cart items
            for cart_item in cart_items:
                cart_count += cart_item.quantity

        except Cart.DoesNotExist:
            cart_count = 0 
    return dict(cart_count=cart_count)