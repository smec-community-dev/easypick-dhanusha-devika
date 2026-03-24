from django.urls import path
from .import views

urlpatterns = [
    path('', views.main_home, name='mainhome'),
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name='logout'),
    # path('shop/',views.shop_view,name='shop'),
    # path('adminlogin/',views.admin_view,name='admin_login'),
]