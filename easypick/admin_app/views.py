
from django.shortcuts import render, redirect
from seller.models import SellerProfile,Product
from customer.models import Order,OrderItem
from django.db.models import Q
from django.http import JsonResponse



def admin_dashboard_view(request):

    query = request.GET.get("q")

    if request.user.role == "ADMIN":
        return redirect("admin_dashboard")

    total_sellers = SellerProfile.objects.count()
    total_products = Product.objects.count()
    orders = Order.objects.select_related('customer').order_by('-order_date')
    sellers = SellerProfile.objects.all()

    if query:
        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )

        sellers = sellers.filter(
            Q(store_name__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__username__icontains=query)
        )
    orders = orders[:10]

    data = {
        "total_sellers": total_sellers,
        "total_products": total_products,
        "orders": orders,
        "sellers": sellers,
    }

    return render(request, "admin/admindashboard.html", data)

def seller_management(request):
    status = request.GET.get("status", "PENDING")
    search = request.GET.get("search", "")

    # Base queryset
    sellers = SellerProfile.objects.all()

    # Apply search filter
    if search:
        sellers = sellers.filter(
            Q(store_name__icontains=search) |
            Q(user__username__icontains=search)
        )
    else:
        sellers = sellers.filter(status=status)

    # Status tabs for filter bar
    status_tabs = [
        {"key": "PENDING", "label": "Pending"},
        {"key": "APPROVED", "label": "Approved"},
        {"key": "REJECTED", "label": "Rejected"},
    ]

    context = {
        "sellers": sellers,
        "status": status,
        "search": search,
        "status_tabs": status_tabs,
    }

    return render(request, "admin/sellermanage.html", context)


def approve_seller(request, seller_id):
    seller = SellerProfile.objects.get(id=seller_id)
    seller.status = "APPROVED"
    seller.save()
    return redirect("seller_management")


def reject_seller(request, seller_id):
    seller = SellerProfile.objects.get(id=seller_id)
    seller.status = "REJECTED"
    seller.save()
    return redirect("seller_management")
def search_sellers(request):

    query = request.GET.get("q")

    sellers = SellerProfile.objects.filter(store_name__icontains=query)[:5]

    data = []

    for seller in sellers:
        data.append({
            "name": seller.user.username,
            "store": seller.store_name,
            "email": seller.user.email
        })

    return JsonResponse(data, safe=False)

def product_management(request):
    # Get current status from query params, default to 'PENDING'
    status = request.GET.get("status", "PENDING")
    search = request.GET.get("search", "")

    # Start with all products
    products = Product.objects.all()

    # Filter products by search term
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(seller__store_name__icontains=search)
        )
    else:
        # If no search term, filter by status
        products = products.filter(status=status)

    # Status tabs for template
    status_tabs = [
        {'key': 'PENDING', 'label': 'Pending'},
        {'key': 'APPROVED', 'label': 'Approved'},
        {'key': 'REJECTED', 'label': 'Rejected'},
    ]

    context = {
        "products": products,
        "status": status,
        "search": search,
        "status_tabs": status_tabs,
    }

    return render(request, "admin/productsmanagement.html", context)


def approve_product(request, product_id):

    product = Product.objects.get(id=product_id)
    product.status = "APPROVED"
    product.save()

    return redirect("product_approvals")


def reject_product(request, product_id):

    product = Product.objects.get(id=product_id)
    product.status = "REJECTED"
    product.save()

    return redirect("product_approvals")

def order_management(request):
    status = request.GET.get("status", "All")
    search = request.GET.get("search", "")

    # Build the queryset
    if status != "All":
        orders = Order.objects.filter(status=status).select_related("customer")
    else:
        orders = Order.objects.all().select_related("customer")
    
    if search:
        orders = orders.filter(
            Q(order_id__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(phone__icontains=search)
        )

    # # Define status filter tabs
    # status_tabs = [
    #     {'key': 'All', 'label': 'All'},
    #     {'key': 'Pending', 'label': 'Pending'},
    #     {'key': 'Confirmed', 'label': 'Confirmed'},
    #     {'key': 'Delivered', 'label': 'Delivered'},
    # ]

    context = {
        "orders": orders,
        "status": status,
        "search": search,
        # "status_tabs": status_tabs,
    }

    return render(request, "admin/ordermanagement.html", context)
def ship_order(request, order_id):

    order = Order.objects.get(id=order_id)
    order.status = "SHIPPED"
    order.save()

    return redirect("order_management")

def deliver_order(request, order_id):

    order = Order.objects.get(id=order_id)
    order.status = "DELIVERED"
    order.save()

    return redirect("order_management")

def cancel_order(request, order_id):

    order = Order.objects.get(id=order_id)
    order.status = "CANCELLED"
    order.save()
    return redirect("order_management")