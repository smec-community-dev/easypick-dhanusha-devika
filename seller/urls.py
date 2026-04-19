from django.urls import path
from .import views

urlpatterns = [
    # path('seller_register/',views.seller_register_view,name='seller_register'),
    # path('seller_dashboard/',views.seller_dashboard),
   
    path("sellerregister/", views.seller_register, name="seller_register"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    # path("sellerlogin/", views.seller_login, name="seller_login"),
    # path('google-login/', views.seller_google_login, name='seller_google_login'),
    path("logout/", views.seller_logout, name="seller_logout"),
    path("profile/", views.seller_profileview, name="seller_profile"),
    path("edit-profile/", views.editprofile_view, name="edit_profile"),
    path("sellerdashboard/", views.seller_dashboard, name="seller_dashboard"),
    path('pending/', views.seller_pending, name='seller_pending'),
    path("add-product/", views.addproduct_view, name="add_product"),
    path("load-subcategories/", views.load_subcategories, name="load_subcategories"),
    # path('load-attributes/', views.load_attributes, name="load_attributes"),
    path("edit-product/<int:product_id>/<int:variant_id>/", views.edit_product_view, name="edit_product"),
    path("delete-product/<int:product_id>/", views.delete_product_view, name="delete_product"),
    path( "seller/products/",views.product_list_view,name="product_list"),
    path('product-status/<int:product_id>/', views.product_status_ajax, name='product_status_ajax'),
    path('orders/', views.orderlist_view, name='order_list'),
    path("update-order-status/<int:order_id>/",views.update_order_status,name="update_order_status"),
    # path("seller-discounts/", views.seller_discount_view, name="seller_discounts"),
    # path("add-discount/", views.add_discount_view, name="add_discount"),
    # path('discounts/', views.variant_discount_list, name='variant_discount_list'),
    path('inventory-log/', views.inventory_log_view, name='inventory_log'),
    path('restock/<int:variant_id>/', views.restock_form_view, name='restockform'),
    path('adjustment/<int:variant_id>/', views.adjustment_form_view, name='adjustmentform'),
    path('reviews/', views.seller_reviews, name='seller_reviews'),

]

