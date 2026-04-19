from django.db.models.functions import ExtractMonth
from django.db.models import Sum
from django.shortcuts import render, redirect,get_object_or_404
from seller.models import SellerProfile,Product
from customer.models import Order,OrderItem
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from core.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.utils.text import slugify
from datetime import timedelta

@login_required
def admin_dashboard_view(request):

    if not (request.user.is_superuser or request.user.role == "ADMIN"):
        return redirect("mainhome")   # NOT login

    query = request.GET.get("q")

    total_sellers = SellerProfile.objects.count()
    total_products = Product.objects.count()
    orders = Order.objects.select_related('customer').order_by('-order_date')
    sellers = SellerProfile.objects.all()
    total_sales = Order.objects.filter(
    status__iexact="delivered"
    ).aggregate(total=Sum('total_amount'))['total'] or 0
# Monthly Sales Data
    monthly_sales = (
    Order.objects
    .annotate(month=ExtractMonth('order_date'))
    .values('month')
    .annotate(total=Sum('total_amount'))
    .order_by('month')
)

# Initialize 12 months
    sales_data = [0] * 12

    for item in monthly_sales:
        month_index = item['month'] - 1
        sales_data[month_index] = float(item['total'])

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
        "sales_data": sales_data, 
         "total_sales": total_sales,
    }

    return render(request, "admin-app/admindashboard.html", data)

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

    return render(request, "admin-app/sellermanage.html", context)


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

    return render(request, "admin-app/productsmanagement.html", context)


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

    return render(request, "admin-app/ordermanagement.html", context)
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




# dhanusha admin


def user_view(request):

    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')

    users = User.objects.all().order_by('-id')

    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )

    total_user = users.count()
    active = users.filter(is_active=True).count()
    pending = users.filter(is_active=False).count()

    new_this_week = users.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()

    context = {
        "count": total_user,
        "active": active,
        "pending": pending,
        "new_this_week": new_this_week,
        "user": users
    }

    return render(request, 'admin-app/admin_user.html', context)

    return render(request, 'admin-app/admin_user.html', context)

def add_user(request):
    if request.method=="POST":
        user=User()
        user.username=request.POST.get('username')
        user.password=request.POST.get('password')
        user.first_name=request.POST.get('first_name')
        user.last_name=request.POST.get('last_name')
        user.email=request.POST.get('email')
        image = request.FILES.get('profiley_image')
        if image:
            user.profile_image = image
        user.role=request.POST.get('role')
        user.phone_number=request.POST.get('phone_number')
        dob = request.POST.get('dob')
        if dob:
            user.dob=dob
        user.save()
        return redirect('admin_user')
    return render(request,'admin-app/add_user.html')

def toggle_user_status(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            messages.success(request, f'User {"blocked" if user.is_active == False else "unblocked"} successfully!')
        except User.DoesNotExist:
            messages.error(request, 'User not found!')
    
    return redirect('admin_user')



from django.db.models import Q

def admin_category(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')

    categories = Category.objects.prefetch_related('subcategory_set').all()

    # 🔍 SEARCH FEATURE
    query = request.GET.get('q')
    if query:
        categories = categories.filter(
            Q(category_name__icontains=query) |
            Q(slug__icontains=query)
        )

    category_id = request.GET.get('category_id')
    subcategories = None
    selected_category = None

    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            subcategories = selected_category.subcategory_set.all()

        except Category.DoesNotExist:
            subcategories = None

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': selected_category
    }

    return render(request, 'admin-app/admin_category.html', context)
def add_category(request):
    categories = Category.objects.all()
    if request.method == "POST":
        category = Category()
        category.category_name = request.POST.get("category_name")
        category.category_description = request.POST.get("category_description")
        image = request.FILES.get('category_image')
        if image:
            category.category_image = image
        category.created_at = request.POST.get("created_at")
        category.slug = request.POST.get("slug")
        category.is_active = '_save' in request.POST or '_addanother' in request.POST or '_continue' in request.POST
        category.save()
        
        parent_id = request.POST.get('category')
        if parent_id:
            from core.models import SubCategory
            subcategory = SubCategory()
            subcategory.category_id = int(parent_id)
            subcategory.subcategory_name = category.category_name
            subcategory.subcategory_description = category.category_description
            subcategory.subcategory_image = category.category_image
            subcategory.created_at = category.created_at
            subcategory.slug = category.slug
            subcategory.is_active = True
            subcategory.save()
            messages.success(request, f'Subcategory "{category.category_name}" added under parent category!')
        else:
            messages.success(request, 'Category added successfully!')
        
        if '_addanother' in request.POST:
            messages.info(request, 'Ready to add another!')
            return render(request, 'admin/add_category.html', {'categories': categories})
        elif '_continue' in request.POST:
            messages.info(request, 'Continue editing form.')
            return render(request, 'admin/add_category.html', {'categories': categories})
        else:
            return redirect('admin_category')
    
    return render(request, 'admin-app/add_category.html', {'categories': categories})

def delete_category(request,id):
    categroy=Category.objects.get(id=id)
    categroy.delete()
    return redirect('admin_category')





def edit_category(request, category_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')
    
    category = Category.objects.get(id=category_id)
    
    if request.method == 'POST':
        category.category_name = request.POST.get('category_name')
        category.category_description = request.POST.get('category_description')
        if 'category_image' in request.FILES:
            category.category_image = request.FILES['category_image']
        category.slug = request.POST.get('slug')
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_category')
    
    return render(request, 'admin-app/edit_category.html', {'category': category})



def add_subcategory(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')

    categories = Category.objects.all()

    if request.method == "POST":
        parent_id = request.POST.get('category')
        name = request.POST.get('subcategory_name')
        description = request.POST.get('subcategory_description')

        if not parent_id or not name:
            messages.error(request, "Please fill all required fields")
            return redirect('add_subcategory')
        slug = slugify(name)

        original_slug = slug
        counter = 1
        while SubCategory.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        subcategory = SubCategory(
            category_id=parent_id,
            subcategory_name=name,
            subcategory_description=description,
            slug=slug,
            is_active='is_active' in request.POST
        )
        image = request.FILES.get('subcategory_image')
        if image:
            subcategory.subcategory_image = image

        subcategory.save()

        messages.success(request, "Subcategory added successfully! 🎉")
        return redirect('admin_category')

    return render(request, 'admin-app/add_subcategory.html', {
        'categories': categories
    })

def edit_subcategory(request, subcategory_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')

    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    categories = Category.objects.all()

    if request.method == "POST":
        parent_id = request.POST.get('category')
        name = request.POST.get('subcategory_name')
        description = request.POST.get('subcategory_description')

        if not parent_id or not name:
            messages.error(request, "Please fill all required fields")
            return redirect('edit_subcategory', subcategory_id=subcategory.id)
        subcategory.category_id = parent_id
        subcategory.subcategory_name = name
        subcategory.subcategory_description = description
        new_slug = slugify(name)
        if new_slug != subcategory.slug:
            original_slug = new_slug
            counter = 1
            while SubCategory.objects.filter(slug=new_slug).exclude(id=subcategory.id).exists():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            subcategory.slug = new_slug
        image = request.FILES.get('subcategory_image')
        if image:
            subcategory.subcategory_image = image
        subcategory.is_active = 'is_active' in request.POST

        subcategory.save()

        messages.success(request, "Subcategory updated successfully! ✨")
        return redirect('admin_category')

    return render(request, 'admin-app/edit_subcategory.html', {
        'subcategory': subcategory,
        'categories': categories
    })

def delete_subcategory(request, subcategory_id):
    subcategory=SubCategory.objects.get(id=subcategory_id)
    subcategory.delete()
    return redirect('admin_category')