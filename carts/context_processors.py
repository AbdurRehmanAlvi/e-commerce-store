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
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user) # This Will give you cart irems on base of user id.
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1]) # Means filter by cart id. [:1] in case of many cart id's this will give you only one cart id
            # Check Numbers of cart items
            for cart_item in cart_items:
                cart_count += cart_item.quantity

        except Cart.DoesNotExist:
            cart_count = 0 
    return dict(cart_count=cart_count)