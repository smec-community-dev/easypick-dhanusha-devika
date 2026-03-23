from django.contrib import admin
from .models import (
    Cart,
    CartItems,
    Wishlist,
    Review,
    Order,
    OrderItem,
)

admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)