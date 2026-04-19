from django.contrib import admin
from .models import (
    User,
    Address,
    Notification,
    Category,
    SubCategory,
   
)

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Notification)
admin.site.register(Category)
admin.site.register(SubCategory)
