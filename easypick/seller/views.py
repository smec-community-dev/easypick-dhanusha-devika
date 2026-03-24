from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from core.models import *
from customer.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.text import slugify
from .models import Product, ProductVariant, ProductImage, SellerProfile
from core.models import SubCategory,Category
from customer.models import  OrderItem ,Order
from .models import Attribute, AttributeOption, ProductVariant, VariantAttributeBridge
from django.http import JsonResponse
from .models import Discount
from django.db.models import Prefetch
from seller.models import InventoryLog
from customer.models import Order
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import uuid
from .models import ProductVariant
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random
from django.contrib.auth.password_validation import validate_password 
from .models import SellerProfile 
from django.db.models import Avg, Count
from django.db.models import Sum
from customer.models import Review
sku = "SKU-" + str(uuid.uuid4())[:8]



def seller_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")  

        store_name = request.POST.get("store_name")
        gst_number = request.POST.get("gst_number")
        pan_number = request.POST.get("pan_number")
        bank_account_number = request.POST.get("bank_account_number")
        ifsc_code = request.POST.get("ifsc_code")
        business_address = request.POST.get("business_address")

        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format")
            return redirect("seller_register")

       
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("seller_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("seller_register")

        
        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("seller_register")

        try:
            validate_password(password)  
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return redirect("seller_register")

        user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        )
        user.is_active = False      
        user.role = "SELLER"       
        user.save()
      
        seller = SellerProfile.objects.create(
            user=user,
            store_name=store_name,
            store_slug=slugify(store_name),
            gst_number=gst_number,
            pan_number=pan_number,
            bank_account_number=bank_account_number,
            ifsc_code=ifsc_code,
            business_address=business_address
        )

      
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['email'] = email

        
        send_mail(
            "EasyPick OTP Verification",
            f"Hello {store_name},\n\nYour OTP is: {otp}\n\nPlease enter this code to verify your account.\n\nRegards,\nEasyPick Team",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "Seller registered successfully. Check your email for OTP.")
        return redirect("verify_otp")

    return render(request, "seller/sellerregistration.html")

def verify_otp(request):
    if request.method == "POST":
        otp = (
            request.POST.get("d1","") +
            request.POST.get("d2","") +
            request.POST.get("d3","") +
            request.POST.get("d4","") +
            request.POST.get("d5","") +
            request.POST.get("d6","")
        )

        session_otp = request.session.get("otp")

        if otp == session_otp:
            email = request.session.get("email")
            if email:
                try:
                    user = User.objects.get(email=email)
                    user.is_active = True
                    user.save()

                   
                    request.session.pop('otp', None)
                    request.session.pop('email', None)

                    messages.success(request, "OTP verified. Please login now.")
                    return redirect("login") 
                except User.DoesNotExist:
                    messages.error(request, "User not found. Please register again.")
                    return redirect("seller_register")
            else:
                messages.error(request, "Session expired. Please register again.")
                return redirect("seller_register")
        else:
            messages.error(request, "Invalid OTP")
            return redirect("verify_otp") 

   
    return render(request, "seller/otpverification.html")

def resend_otp(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Session expired. Please register again.")
        return redirect("seller_register")
    
   
    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp

  
    send_mail(
        "EasyPick OTP Verification",
        f"Your OTP for EasyPick verification is: {otp}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_otp")

# def seller_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate( request,username=username,password=password)

#         if user :
#             login(request, user)
#             messages.success(request, "Login successful")
#             return redirect("seller_dashboard")
#         else:
#             messages.error(request, "Invalid credentials")

#     return render(request, "seller/sellerlogin.html")


# def seller_google_login(request):
#     request.session['is_seller_login'] = True
#     return redirect('/accounts/google/login/')

def seller_logout(request):
    logout(request)
    return redirect("seller_login")

@role_required("SELLER")
@login_required
def seller_profileview(request):
    seller = request.user.seller_profile

    data = {
        "seller": seller
    }
    return render(request, "seller/sellerprofile.html", data)


@role_required("SELLER")
@login_required
def editprofile_view(request):
    seller = request.user.seller_profile
    if request.method == "POST":
        seller.store_name = request.POST.get("store_name")
        seller.gst_number = request.POST.get("gst_number")
        seller.pan_number = request.POST.get("pan_number")
        seller.bank_account_number = request.POST.get("bank_account")
        seller.ifsc_code = request.POST.get("ifsc_code")
        seller.business_address = request.POST.get("address")
        seller.save()

        return redirect("seller_profile")

    data = {
        "seller": seller
    }

    return render(request, "seller/editsellerprofile.html", data)


@role_required("SELLER")
@login_required
def seller_dashboard(request):
    seller_profile = getattr(request.user, "seller_profile", None)

   
    if not seller_profile:
        return redirect("seller_register") 


    if seller_profile.status != "APPROVED":
        return redirect("seller_pending")

   
    query = request.GET.get("q")


    seller_products = Product.objects.filter(
        seller=seller_profile
    ).order_by('-created_at')

   
    orders = Order.objects.filter(
        items__product__seller=seller_profile
    ).distinct().order_by('-order_date')

   
    if query:
        seller_products = seller_products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )

    
    total_products = seller_products.count()
    total_orders = orders.count()
    total_revenue = Order.objects.filter(
        items__product__seller=seller_profile,
        status="DELIVERED"
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    low_stock_count = ProductVariant.objects.filter(
        product__seller=seller_profile,
        stock_quantity__lt=5
    ).count()

    
    orders = orders[:5]

    data = {
        "products": seller_products,
        "total_products": total_products,
        "seller": seller_profile,
        "orders": orders,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "low_stock_count": low_stock_count,
    }

    return render(request, "seller/seller_dashboard.html", data)

@login_required
def seller_pending(request):
    seller_profile = getattr(request.user, 'seller_profile', None)

    if not seller_profile:
        return redirect('seller_register')

   
    if seller_profile.status == "APPROVED":
        return redirect('seller_dashboard')  

    return render(request, 'seller/pending.html')
def generate_unique_sku():
    while True:
        sku = "SKU-" + str(uuid.uuid4())[:8]
        if not ProductVariant.objects.filter(sku_code=sku).exists():
            return sku

import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import (
    Product, ProductVariant, ProductImage, InventoryLog,
    VariantAttributeBridge, Category, SubCategory, Attribute
)

# --- Helper to generate unique SKU ---
def generate_unique_sku():
    while True:
        sku = "SKU-" + str(uuid.uuid4())[:8]
        if not ProductVariant.objects.filter(sku_code=sku).exists():
            return sku

@login_required
def addproduct_view(request):
    seller_profile = request.user.seller_profile
    categories = Category.objects.filter(is_active=True)
    subcategories = SubCategory.objects.filter(is_active=True)
    attributes = Attribute.objects.prefetch_related("options").all()

    if request.method == "POST":
        # --- Category & Subcategory ---
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        if not category_id:
            messages.error(request, "Please select a category.")
            return redirect("add_product")

        category = Category.objects.get(id=category_id)
        subcategory = SubCategory.objects.get(id=subcategory_id) if subcategory_id else None

        # --- Product Info ---
        name = request.POST.get("name")
        brand = request.POST.get("brand")
        description = request.POST.get("description")

        product = Product.objects.create(
            seller=seller_profile,
            subcategory=subcategory,
            name=name,
            slug=slugify(name),
            brand=brand,
            description=description,
            approval_status="PENDING"
        )

        # --- SKU Handling (always generate unique SKU) ---
        sku_code = generate_unique_sku()

        # --- Product Variant Creation with IntegrityError catch ---
        try:
            variant = ProductVariant.objects.create(
                product=product,
                sku_code=sku_code,
                mrp=float(request.POST.get("mrp") or 0),
                selling_price=float(request.POST.get("selling_price") or 0),
                cost_price=float(request.POST.get("cost_price") or 0),
                stock_quantity=int(request.POST.get("stock_quantity") or 0),
                weight=float(request.POST.get("weight") or 0),
                length=float(request.POST.get("length") or 0),
                width=float(request.POST.get("width") or 0),
                height=float(request.POST.get("height") or 0),
                tax_percentage=float(request.POST.get("tax_percentage") or 0),
            )
        except IntegrityError:
            messages.error(request, "SKU collision occurred! Try again.")
            product.delete()  # remove product if variant fails
            return redirect("add_product")

        # --- Inventory Log ---
        initial_stock = variant.stock_quantity
        if initial_stock > 0:
            InventoryLog.objects.create(
                variant=variant,
                change_amount=initial_stock,
                reason="Initial stock",
                performed_by=request.user
            )

        # --- Variant Attributes ---
        selected_options = request.POST.getlist("attribute_options")
        for option_id in selected_options:
            VariantAttributeBridge.objects.create(
                variant=variant,
                option_id=option_id
            )

        # --- Product Image ---
        image = request.FILES.get("images")  # ensure your HTML input name="images"
        if image:
            ProductImage.objects.create(
                variant=variant,
                image=image,
                alt_text=name,
                is_primary=True
            )

        messages.success(request, "Product added successfully!")
        return redirect("product_list")

    # --- GET Request ---
    data = {
        "categories": categories,
        "subcategories": subcategories,
        "attributes": attributes
    }
    return render(request, "seller/addprod.html", data)


def load_subcategories(request):

    category_id = request.GET.get("category_id")

    subcategories = SubCategory.objects.filter(
        category_id=category_id,
        is_active=True
    ).values("id", "subcategory_name")

    return JsonResponse(list(subcategories), safe=False)

# def load_attributes(request):

#     subcategory_id = request.GET.get("subcategory_id")

#     attributes = Attribute.objects.filter(
#         subcategory_id=subcategory_id
#     ).prefetch_related("options")

#     data = []

#     for attr in attributes:
#         data.append({
#             "id": attr.id,
#             "name": attr.name,
#             "options": [
#                 {"id": opt.id, "value": opt.value}
#                 for opt in attr.options.all()
#             ]
#         })

#     return JsonResponse(data, safe=False)
@login_required
def edit_product_view(request, product_id, variant_id):

    seller_profile = request.user.seller_profile

    product = get_object_or_404(Product, id=product_id, seller=seller_profile)
    variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
    categories = Category.objects.filter(is_active=True)
    subcategories = SubCategory.objects.filter(is_active=True)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.slug = slugify(product.name)
        product.subcategory_id = request.POST.get("subcategory")
        product.description = request.POST.get("description")
        product.brand = request.POST.get("brand")
        product.model_number = request.POST.get("model_number")
        product.save()
        variant.sku_code = request.POST.get("sku_code")

        variant.mrp = float(request.POST.get("mrp") or 0)
        variant.selling_price = float(request.POST.get("selling_price") or 0)
        variant.cost_price = float(request.POST.get("cost_price") or 0)

        variant.stock_quantity = int(request.POST.get("stock_quantity") or 0)

        variant.weight = float(request.POST.get("weight") or 0)
        variant.length = float(request.POST.get("length") or 0)
        variant.width = float(request.POST.get("width") or 0)
        variant.height = float(request.POST.get("height") or 0)

        variant.tax_percentage = 0
        variant.save()


        image = request.FILES.get("image")

        if image:
            ProductImage.objects.create(
                variant=variant,
                image=image, 
                is_primary=True
            )

        return redirect("seller_dashboard")

  
    data = {
        "product": product,
        "variant": variant,
        "subcategories": subcategories,
        "categories": categories,  
    }

    return render(request, "seller/editproduct.html", data)


@login_required
def delete_product_view(request, product_id):
    seller_profile = request.user.seller_profile
    product = get_object_or_404(
        Product,
        id=product_id,
        seller=seller_profile
    )
    if request.method == "POST":
        product.delete()
        return redirect("product_list") 

    return redirect("product_list")



def product_list_view(request):
    seller_profile = request.user.seller_profile
    
    stock_filter = request.GET.get("stock")
    search_query = request.GET.get("q")

    products = Product.objects.filter(
        seller=seller_profile
    ).order_by("-created_at")

    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(variants__sku_code__icontains=search_query)
        ).distinct()

    
    if stock_filter == "in":
        products = products.filter(variants__stock_quantity__gt=0)

    elif stock_filter == "out":
        products = products.filter(variants__stock_quantity=0)

    data = {
        "products": products,
        "stock_filter": stock_filter
    }

    return render(request, "seller/productlist.html",data)


@login_required
def product_status_ajax(request, product_id):
    seller_profile = request.user.seller_profile
    try:
        product = Product.objects.get(id=product_id, seller=seller_profile)
        return JsonResponse({"status": product.approval_status})
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

@login_required
def orderlist_view(request):
    seller_profile = request.user.seller_profile

    status = request.GET.get("status")
    search_query = request.GET.get("q")

    orders = Order.objects.filter(
        items__product__seller=seller_profile
    ).distinct().order_by("-order_date")

    if status:
        orders = orders.filter(status=status)

    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
   

    data = {
        "orders": orders,
        "total_orders": orders.count(),
        "pending_orders": orders.filter(status="PENDING").count(),
        "shipped_orders": orders.filter(status="SHIPPED").count(),
        "delivered_orders": orders.filter(status="DELIVERED").count(),
        "cancelled_orders": orders.filter(status="CANCELLED").count(),
    }
    return render(request, "seller/seller_order.html", data)


def update_order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == "POST":
        new_status = request.POST.get("status")

        order.status = new_status
        order.save()
    return redirect("order_list")

@login_required
def seller_discount_view(request):

    seller = request.user.seller_profile

    discounts = Discount.objects.filter(seller=seller).select_related("variant")

    data = {
        "discounts": discounts
    }

    return render(request, "seller/seller_discount.html", data)

@login_required
def add_discount_view(request):

    seller = request.user.seller_profile
    variants = ProductVariant.objects.filter(product__seller=seller)

    if request.method == "POST":

        variant_id = request.POST.get("variant")
        discount_percent = request.POST.get("discount_percent")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        variant = ProductVariant.objects.get(id=variant_id)

        Discount.objects.create(
            seller=seller,
            variant=variant,
            discount_percent=discount_percent,
            start_date=start_date,
            end_date=end_date
        )

        return redirect('variant_discount_list')

    return render(request,"seller/add_discount.html",{"variants":variants})


def variant_discount_list(request):
   
    variants = ProductVariant.objects.prefetch_related(Prefetch('discount_set', queryset=Discount.objects.all())).all()
    
    return render(request, "seller/variantlist.html", {"variants": variants})


def inventory_log_view(request):

    search_query = request.GET.get("q")
    filter_type = request.GET.get("type")
    variants = ProductVariant.objects.filter(
        product__seller=request.user.seller_profile
    ).select_related("product")

    logs = InventoryLog.objects.filter(
        variant__product__seller=request.user.seller_profile
    ).select_related(
        "variant", "variant__product", "performed_by"
    ).order_by("-created_at")


    if search_query:
        logs = logs.filter(
            Q(variant__sku_code__icontains=search_query) |
            Q(variant__product__name__icontains=search_query)
        )

 
    if filter_type == "restock":
        logs = logs.filter(reason="Restock")

    elif filter_type == "sales":
        logs = logs.filter(reason="Sales")

    elif filter_type == "adjustment":
        logs = logs.filter(reason="Adjustment")

    data = {
        "logs": logs,
        "variants": variants,
        "filter_type": filter_type
    }

    return render(request, "seller/inventory_log.html", data)


@login_required
def restock_form_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    current_stock = variant.logs.aggregate(total=models.Sum('change_amount'))['total'] or 0

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 0))
        reason = request.POST.get("reason", "")
        note = request.POST.get("note", "")

        if quantity > 0:
            InventoryLog.objects.create(
                variant=variant,
                change_amount=quantity,
                reason=reason,
                performed_by=request.user,
            
            )
        return redirect('inventory_log')

    data = {
        "variant": variant,
        "current_stock": current_stock,
    }
    return render(request, "seller/restockform.html", data)


@login_required
def adjustment_form_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
   
    current_stock = InventoryLog.objects.filter(variant=variant).aggregate(
        total=Sum('change_amount')
    )['total'] or 0

    if request.method == "POST":
        adjustment_type = request.POST.get("adjustment_type")
        quantity = int(request.POST.get("quantity", 0))
        reason = request.POST.get("reason")
        if quantity > 0 and adjustment_type in ["add", "remove"]:
           
            change_amount = quantity if adjustment_type == "add" else -quantity

            InventoryLog.objects.create(
                variant=variant,
                change_amount=change_amount,
                reason=reason,
                performed_by=request.user,
            )

        return redirect('inventory_log')

    data = {
        "variant": variant,
        "current_stock": current_stock
    }
    return render(request, "seller/adjustmentform.html", data)


@login_required
def seller_reviews(request):
    seller = getattr(request.user, 'seller_profile', None)
    if not seller:
        return redirect('home')


    products = Product.objects.filter(seller=seller)

    
    all_reviews = Review.objects.filter(product__in=products)

 
    rating_filter = request.GET.get('rating')
    reviews = all_reviews
    if rating_filter:
        reviews = all_reviews.filter(rating=int(rating_filter))

   
    total_reviews = all_reviews.count()  

  
    avg_rating = all_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

  
    rating_counts = all_reviews.values('rating').annotate(count=Count('rating'))

  
    rating_dict = {i: 0 for i in range(1, 6)}
    for item in rating_counts:
        rating_dict[item['rating']] = item['count']

  
    rating_percentage = {
        i: round((rating_dict[i] / total_reviews) * 100) if total_reviews else 0
        for i in range(1, 6)
    }

    context = {
        'reviews': reviews,  
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'rating_percentage': rating_percentage,
        'selected_rating': rating_filter,
    }

    return render(request, 'seller/reviewpage.html', context)