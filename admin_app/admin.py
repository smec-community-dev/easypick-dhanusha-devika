from django.contrib import admin
from .models import (
    Offer,
    # Discount,
    Coupon,
   
)

admin.site.register(Offer)
# admin.site.register(Discount)
admin.site.register(Coupon)

# Register your models here.