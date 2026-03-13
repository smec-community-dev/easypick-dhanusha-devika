from django.urls import path
from . import views

urlpatterns = [
    path('',views.main_home_view,name="main_home"),
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name='logout'),
    path('admin_login/',views.admin_view,name="admin_login"),
    path('shop/',views.shop_view,name='shop'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
]
