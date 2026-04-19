from customer.models import Cart  # change if Cart is in another app

def cart_count(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(customer=request.user)
    else:
        cart_items = []

    return {
        'cart_item': cart_items
    }