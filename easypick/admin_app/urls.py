from django.urls import path
from . import views

urlpatterns = [
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('admin_user/',views.user_view,name='admin_user'),
    path('admin_category/',views.admin_category,name='admin_category'),
    path('add_category/',views.add_category,name='add_category'),
]
