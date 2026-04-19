from django.urls import path
from . import views

urlpatterns = [
    

path("admin-dashboard", views.admin_dashboard_view, name="admin_dashboard"),
    path("seller-management/", views.seller_management, name="seller_management"),
    path("approve-seller/<int:seller_id>/", views.approve_seller, name="approve_seller"),
    path("reject-seller/<int:seller_id>/", views.reject_seller, name="reject_seller"),
    path("product-approvals/", views.product_management, name="product_approvals"),
    path("approve-product/<int:product_id>/", views.approve_product, name="approve_product"),
    path("reject-product/<int:product_id>/", views.reject_product, name="reject_product"),
    path("orders/", views.order_management, name="order_management"),
    path("ship-order/<int:order_id>/", views.ship_order, name="ship_order"),
    path("deliver-order/<int:order_id>/", views.deliver_order, name="deliver_order"),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("search-sellers/", views.search_sellers, name="search_sellers"),

    path('admin_user/',views.user_view,name='admin_user'),
    path('add_user/',views.add_user,name='add_user'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin_category/',views.admin_category,name='admin_category'),
    path('delete_category/<int:id>/',views.delete_category,name='delete_category'),
    path('add_category/',views.add_category,name='add_category'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('add_subcategory/',views.add_subcategory,name='add_subcategory'),
    path('edit-subcategory/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('delete_subcategory/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),


]
