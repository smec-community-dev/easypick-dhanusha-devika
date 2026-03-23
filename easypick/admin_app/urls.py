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





]