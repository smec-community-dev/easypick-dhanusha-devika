from django.contrib import admin
from .models import (
    Cart,
    CartItems,
    Wishlist,
    WishlistItems,
    Review,
    Order,
    OrderItem,
    OrderHistory,
    ReviewImage,
    
)

admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(WishlistItems)
admin.site.register(ReviewImage)
admin.site.register(OrderHistory)