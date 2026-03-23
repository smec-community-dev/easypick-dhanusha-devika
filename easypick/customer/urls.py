from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/',views.home_view,name='home'),
    path('register/',views.customer_register_view,name='customer_register'),
    path('customer/profile/', views.customer_profile_update_view, name='customer_profile'),
    path('cart/',views.cart_view,name='cart'),
    path('wishlist/',views.wishlist_view,name='wishlist'),
    path('customer_dashboard/',views.customer_dashboard_view,name='customer_dashboard'),
    path('add_address/',views.add_address_view,name='add_address'),
    path('delete_address/<int:id>',views.delete_address,name='delete_address'),
    path('update_address/<int:id>',views.update_address,name='update_address'),
    path('account_security/',views.account_security_view,name='account_security'),
    path('customer_notification/',views.customer_notification_view,name='customer_notification'),
    path('customer_order_history/',views.customer_order_history,name='customer_order_history'),
    path('customer_order/',views.customer_order_view,name="customer_order"),
    path('customer_recentlyviewed/',views.customer_recently_viewd,name="customer_recentlyviewed"),
    path('customer_recommentation/',views.customer_recommentation,name="customer_recommentation"),
    path('shop/',views.shop_view,name='shop'),
    path('account_delete/',views.delete_account,name='account_delete'),
    path('account_delete_confirmation/',views.delete_account_confirmation,name='account_delete_confirmation'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)