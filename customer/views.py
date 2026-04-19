import json
import random
import uuid

import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg, Prefetch, Sum, Count
from decimal import Decimal, InvalidOperation

from core.models import *
from seller.models import *
from customer.models import *
from .utils import generate_otp

User = get_user_model()




# Create your views here.
def customer_register_view(request):
    if request.method == "POST":
        form_data = {
            'first_name': request.POST.get("first_name"),
            'last_name': request.POST.get("last_name"),
            'username': request.POST.get("username"),
            'email': request.POST.get("email"),
            'password': request.POST.get("password"),
            'confirm_password': request.POST.get("confirm_password")
        }
        if form_data['password'] != form_data['confirm_password']:
            messages.error(request, 'Password do not match')
            return render(request, 'core/customer_registartion.html')

        if User.objects.filter(email=form_data['email']).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'core/customer_registartion.html')

        if User.objects.filter(username=form_data['username']).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'core/customer_registartion.html')
        otp = str(random.randint(100000, 999999))
        cache.set(form_data['email'], otp, timeout=300)
        request.session['register_data'] = form_data

        send_mail(
            subject="Your OTP Verification Code",
            message=f"Your OTP is {otp}",
            from_email='your_email@gmail.com',
            recipient_list=[form_data['email']],
        )

        return redirect('customer_verify_otp')

    return render(request, 'core/customer_registartion.html')
    
def verify_otp(request):
    register_data = request.session.get('register_data')

    if not register_data:
        messages.error(request, "Session expired. Register again.")
        return redirect('customer_register')

    email = register_data['email']

    if request.method == "POST":
        user_otp = request.POST.get('otp')
        stored_otp = cache.get(email)

        if stored_otp is None:
            messages.error(request, "OTP expired")
            return redirect('customer_register')

        if user_otp == stored_otp:
            user = User.objects.create_user(
                username=register_data['username'],
                email=register_data['email'],
                password=register_data['password'],
                first_name=register_data['first_name'],
                last_name=register_data['last_name']
            )
            user.role = "CUSTOMER"
            user.save()
            send_mail(
            subject="Registration Successful 🎉",
            message=f"""Hello {user.first_name},

        Your account has been successfully created.

        Welcome to EasyPick 🛍️

        Thanks,
        EasyPick Team
        """,
            from_email='your_email@gmail.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
            cache.delete(email)
            del request.session['register_data']

            messages.success(request, "Account created successfully")
            return redirect('login')

        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'customer/verify_otp.html')

def home_view(request):
    products=ProductVariant.objects.all()
    category=Category.objects.all()
    if request.user.is_authenticated:
        cart_item = CartItems.objects.filter(cart__customer=request.user)
        wishlist_item = WishlistItems.objects.filter(wishlist__customer=request.user)
    else:
        cart_item = []
        wishlist_item = []

    return render(request,'customer/home.html',{'data':request.user,'category':category,"products":products,"cart_item":cart_item,"wishlist_item":wishlist_item})

@login_required
def customer_profile_update_view(request):
    address = Address.objects.filter(user=request.user)
    user_data = request.user
    if request.method == "POST":
        
        user_data.first_name = request.POST.get('full_name', "")
        user_data.last_name = request.POST.get('last_name', "")
        user_data.email = request.POST.get('email', "")
        user_data.phone_number = request.POST.get('phone_number')
        dob = request.POST.get('dob')
        if dob:
            user_data.dob=dob
        else:
            user_data.dob=None
        user_data.age = request.POST.get('age')
        user_data.gender = request.POST.get('gender')
        image=request.FILES.get('image')
        if image:
            user_data.profile_image=image
        
        user_data.save()
        
        messages.success(request,'Profile updated successfully')
        return redirect('customer_profile')

    return render(request, 'customer/customer_profile.html', {'user_data': user_data,'address':address})
@login_required(login_url="/login")
def add_address_view(request):
    if request.method=="POST":
        address_obj=Address()
        address_obj.user=request.user
        address_obj.full_name=request.POST.get('full_name')
        address_obj.phone_number=request.POST.get('phone_number')
        address_obj.house_no=request.POST.get('house_no')
        address_obj.landmark=request.POST.get('landmark')
        address_obj.street=request.POST.get('street')
        address_obj.city=request.POST.get('city')
        address_obj.state=request.POST.get('state')
        address_obj.zip_code=request.POST.get('zip_code')
        address_obj.address_type=request.POST.get('address_type')
        address_obj.save()
        return redirect('customer_profile')
    return render(request,'customer/customer_address_add.html')

@login_required
def delete_address(request,id):
    address=Address.objects.get(id=id)
    print(address)
    address.delete()
    return redirect('customer_profile')

@login_required(login_url="/login")
def update_address(request,id):
    address_data=Address.objects.get(id=id)
    if request.method=="POST":
        user=request.user
        address_data.full_name=request.POST.get('full_name')
        address_data.phone_number=request.POST.get('phone_number')
        address_data.house_no=request.POST.get('house_no')
        address_data.landmark=request.POST.get('landmark')
        address_data.street=request.POST.get('street')
        address_data.city=request.POST.get('city')
        address_data.state=request.POST.get('state')
        address_data.zip_code=request.POST.get('zip_code')
        address_data.address_type=request.POST.get('address_type')
        address_data.save()
        return redirect('customer_profile')
    return render(request,'customer/customer_address_add.html',{'address_data':address_data})
@login_required(login_url="/login")
def address_list(request):
    address = Address.objects.filter(user=request.user)
    return render(request,'customer/address_list.html',{'address':address})

@login_required(login_url="/login")
def select_order_address(request, product_id, address_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    address = get_object_or_404(Address, id=address_id, user=request.user)
    request.session[f'order_address_{product_id}'] = address_id
    
    address_str = f"{address.house_no} {address.street}, {address.city}, {address.state}, {address.zip_code}"
    
    return JsonResponse({
        'success': True,
        'address_id': address_id,
        'full_name': address.full_name,
        'address_str': address_str,
        'phone': getattr(request.user, 'phone_number', ''),
        'reload_url': f"/customer/order_confirm/{product_id}/"
    })
@login_required(login_url="/login")
def account_security_view(request):
    user=request.user
    if request.method=="POST":
        print("post")
        new_password=request.POST.get('new_password')
        confirm_password=request.POST.get('confirm_password')
        if new_password== confirm_password:
            user.set_password(new_password)   
            user.save()
            messages.success(request, "Password updated successfully")
            return redirect('login')
        else:
            messages.error(request,"Not match the confirm password")
    return render(request,'customer/change_password.html')

def customer_notification_view(request):
    return render(request,'customer/notification.html')


@login_required(login_url="/login")
def add_wishlist(request, id):
    variant = ProductVariant.objects.get(id=id)

    wishlist, created = Wishlist.objects.get_or_create(customer=request.user)

    WishlistItems.objects.get_or_create(
        wishlist=wishlist,
        product=variant
    )

    return redirect('single', id=id)
@login_required(login_url="/login")
def wishlist(request):
    wishlist = Wishlist.objects.filter(customer=request.user).first()

    if wishlist:
        wishlist_items = WishlistItems.objects.filter(wishlist=wishlist)
    else:
        wishlist_items = []

    return render(request,'customer/customer_wishlist.html',{
        'wishlist_items': wishlist_items
    })
@login_required(login_url="/login")
def wishlist_remove(request, id): 
    wishlist_item = get_object_or_404(WishlistItems, id=id)
    wishlist_item.delete()
    return redirect('wishlist')

from django.http import JsonResponse

@login_required
def toggle_wishlist(request, id):
    """
    Toggle wishlist item: add if not exists, remove if exists
    Returns JSON for AJAX frontend
    """
    try:
        variant = ProductVariant.objects.get(id=id)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    wishlist, created = Wishlist.objects.get_or_create(customer=request.user)
    
    existing_item = WishlistItems.objects.filter(
        wishlist=wishlist,
        product=variant
    ).first()
    
    if existing_item:
       
        existing_item.delete()
        status = "removed"
        in_wishlist = False
    else:
        
        WishlistItems.objects.create(
            wishlist=wishlist,
            product=variant
        )
        status = "added"
        in_wishlist = True
    
    return JsonResponse({
        'status': status,
        'in_wishlist': in_wishlist,
        'variant_id': id
    })

def customer_dashboard_view(request):
    return render(request,'customer/customer_dashboard.html',{'user':request.user})

def customer_order_view(request):
    return render(request,'customer/customer_order.html')

@login_required(login_url="/login")
@login_required(login_url="/login")
def track_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related('customer').prefetch_related('items__product', 'history'), order_id=order_id, customer=request.user)
    order_items = order.items.select_related('product')
    steps = ['Pending', 'Processing', 'Shipped', 'Delivered']

    context = {
        'order': order,
        'order_items': order_items,
        'steps': steps,
    }
    return render(request, 'customer/tracke_order.html', context)

def customer_order_history(request, order_id=None):
    orders = Order.objects.filter(customer=request.user, order_id__gt=0).select_related('customer').prefetch_related('items__product').order_by('-order_date')[:10]
    
    if order_id:
        order = get_object_or_404(orders, id=order_id)
        order_items = order.items.select_related('product')
        context = {
            'order': order,
            'order_items': order_items,
            'orders': orders,
        }
        return render(request, 'customer/order_history.html', context)
    
    context = {
        'orders': orders,
        'has_orders': orders.exists(),
    }
    return render(request, 'customer/order_history.html', context)

def customer_recently_viewd(request):
    return render(request,'customer/customer_recentlyviewd.html')

def customer_recommentation(request):
    return render(request,'customer/customer_recommentation.html')


def shop_view(request):
    products = ProductVariant.objects.all().select_related('product').prefetch_related('images')

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if min_price:
            products = products.filter(selling_price__gte=min_price)
    if max_price:
            products = products.filter(selling_price__lte=max_price)
        

    if sort == "new_arrival":
        products = products.order_by("-id")
    elif sort == "low":
        products = products.order_by("selling_price")
    elif sort == "high":
        products = products.order_by("-selling_price")
    elif sort == "name":
        products = products.order_by("product__name")

    in_wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(customer=request.user).first()
        if wishlist:
            in_wishlist_ids = set(
                WishlistItems.objects.filter(wishlist=wishlist).values_list("product_id", flat=True)
            )

    return render(request, "core/shop.html", {
        "product": products,
        "in_wishlist_ids": in_wishlist_ids,
        "selected_sort": sort,
        "min_price": min_price,
        "max_price": max_price,
    })


#Seller dashboard "Home" link in templates/seller/base.html header uses {% url 'home' %} 
# which points to customer home page.Change it to {% url 'seller_dashboard' %} to fix.

@login_required(login_url="/login")
def delete_account(request):
    if request.method == "GET":
        return render(request, 'core/account_deletion_confirmation.html')
    
    if request.method == "POST":
        password_confirm = request.POST.get('password_confirm')
        user = request.user
        
        if not user.check_password(password_confirm):
            messages.error(request, "Password does not match.")
            return render(request, 'core/account_deletion_confirmation.html')
        
        user.delete()
        messages.success(request, "Account deleted successfully.")
        return redirect('home')
@login_required(login_url="/login")
def delete_account_confirmation(request):
    user=request.user
    user.delete()
    messages.success(request,'deleted account')
    return redirect('/')

def category_view(request,id):
    from django.shortcuts import get_object_or_404
    category = get_object_or_404(Category, id=id)
    products = SubCategory.objects.filter(category=category, is_active=True)
    sort = request.GET.get('sort')
    if sort == "new_arrival":
        products = products.order_by("-created_at")
    elif sort == "low":
        products = products.order_by("id")
    elif sort == "high":
        products = products.order_by("-id")
    elif sort == "name":
        products = products.order_by("subcategory_name")

    context = {
        'category': category,
        'products': products,
        'selected_sort': sort,
        
    }
    return render(request, 'core/category.html', context)

def subcategory_view(request, id):
    
    products = ProductVariant.objects.select_related('product')\
        .prefetch_related('images')\
        .filter(product__subcategory_id=id)

    return render(request, 'core/subcategory.html', {
        'products': products,
        
    })

def single_view(request, id):
  
    product = get_object_or_404(ProductVariant.objects.select_related('product').prefetch_related('images'),id=id)

    if request.method == "POST":
        if request.user.is_authenticated:
            comment = request.POST.get('comment', '').strip()
            rating_str = request.POST.get('rating', '5')
            images = request.FILES.getlist('images')
            
            try:
                rating = int(rating_str)
                if 1 <= rating <= 5:
                    review = Review.objects.create(
                        product=product.product,
                        user=request.user,
                        comments=comment,
                        rating=rating
                    )
                    for img in images:
                        ReviewImage.objects.create(
                            review=review,
                            image=img
                        )
                    messages.success(request, "Review submitted successfully!")
                    return redirect('single', id=id)
                else:
                    messages.error(request, "Rating must be between 1 and 5.")
            except (ValueError, TypeError):
                messages.error(request, "Invalid rating. Please select 1-5 stars.")
        else:
            messages.error(request, "Please log in to submit a review.")
    reviews = Review.objects.filter(
        product=product.product
    ).select_related('user').prefetch_related('images').order_by('-created_at')

    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    rating_counts = dict(reviews.values('rating').annotate(count=Count('rating')).order_by('-rating').values_list('rating', 'count'))
    rating_data = [
        {
            'star': star,
            'percent': int(round((rating_counts.get(star, 0) / total_reviews) * 100)) if total_reviews else 0,
            'count': rating_counts.get(star, 0)
        }
        for star in range(5, 0, -1)
    ]
    
    subcategory = product.product.subcategory
    related_products = ProductVariant.objects.filter(
        product__subcategory=subcategory
    ).exclude(product=product.product).select_related('product').prefetch_related('images')[:8]
    in_wishlist = False
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(customer=request.user).first()
        if wishlist:
            in_wishlist = WishlistItems.objects.filter(
                wishlist=wishlist,
                product=product
            ).exists()
    return render(request, 'core/single_product.html', {
        'product': product,
        'reviews': reviews,
        'in_wishlist': in_wishlist,
        'related_products': related_products,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'rating_data': rating_data,
        'subcategory':subcategory,
    })

@login_required(login_url="/login")
def add_cart(request, id):

    variant = ProductVariant.objects.get(id=id)
    user = request.user

    cart, created = Cart.objects.get_or_create(customer=user)

    try:
        cart_item = CartItems.objects.get(cart=cart, product=variant)
        cart_item.quantity += 1
        cart_item.save()

    except CartItems.DoesNotExist:

        CartItems.objects.create(
            cart=cart,
            product=variant,
            quantity=1
        )

    return redirect('single', id=id)
        

@login_required
def cart_remove(request,id):
    cart_item=CartItems.objects.get(id=id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url="/login")
def cart_view(request):
    cart_user, created = Cart.objects.get_or_create(customer=request.user)
    cart=get_object_or_404(Cart,customer=request.user)
    cart_item = CartItems.objects.filter(cart=cart_user).select_related('product').prefetch_related('product__images')
        
    subtotal = Decimal('0')
    for item in cart_item:
        subtotal += (item.product.selling_price * item.quantity)
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return render(request,'customer/cart.html',{'cart_item':cart_item, 'subtotal': subtotal,'cart':cart})   
    
@login_required
def cart_order(request,id):
    cart=Cart.objects.get(customer=request.user)
    # cart_item=CartItems.objects.filter(cart=cart).select_related('product')
    cart_item=CartItems.objects.filter(cart__customer=request.user).select_related('product')
    address=Address.objects.filter(user=request.user).first()
    subtotal=0
    for item in cart_item:
        subtotal += item.product.selling_price * item.quantity
        total=subtotal+5
        
    addresses = Address.objects.filter(user=request.user)
    return render(request,'customer/cart_orderconfirm.html',{'cart_item':cart_item,'address':address,'addresses':addresses,'subtotal':subtotal,"total":total,"cart":cart})

@login_required(login_url="/login")
def cart_payment(request, id):

    cart = Cart.objects.get(customer=request.user)
    cart_items = cart.items.all()  

    subtotal = 0
    total_quantity = 0

    for item in cart_items:
        subtotal += item.product.selling_price * item.quantity
        total_quantity += item.quantity

    return render(request, 'customer/payment.html', {
        'is_cart': True,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_quantity': total_quantity,
    })

@login_required(login_url="/login")
def order_confirm_view(request, id):
    
    product = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
   
    address = Address.objects.filter(user=request.user)
    
    
    quantity = request.GET.get('qty', 1)
    quantity = int(quantity)
    
    selling_price = product.selling_price
    subtotal = selling_price * quantity

    reviews = product.product.reviews.all()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    review_count = reviews.count()
    
    
    
    context = {
        'product': product,
        'address': address,
        'quantity': quantity,
        'subtotal': subtotal,
        'selling_price': selling_price,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
    }
    return render(request, 'customer/order_confirm.html', context)


def _create_order_master(user, total_amount, payment_method='COD', payment_status='Pending'):
    order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
    return Order.objects.create(
        customer=user,
        order_number=order_number,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status=payment_status,
    )


def _create_order_from_cart(user, payment_method='COD', payment_status='Pending'):
    cart = Cart.objects.filter(customer=user).first()
    if not cart:
        return None

    cart_items = cart.items.select_related('product')
    if not cart_items.exists():
        return None

    total_amount = sum(item.product.selling_price * item.quantity for item in cart_items)
    order = _create_order_master(user, total_amount, payment_method=payment_method, payment_status=payment_status)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product.product,
            quantity=item.quantity,
            price=item.product.selling_price,
        )

    return order


def _create_order_from_single(user, variant, quantity, payment_method='COD', payment_status='Pending'):
    total_amount = variant.selling_price * quantity
    order = _create_order_master(user, total_amount, payment_method=payment_method, payment_status=payment_status)

    OrderItem.objects.create(
        order=order,
        product=variant.product,
        quantity=quantity,
        price=variant.selling_price,
    )

    return order


@login_required(login_url='/login')
def single_payment_view(request, id=None):
    address = Address.objects.filter(user=request.user)
    is_cart = id is None

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method == 'cod':
            if is_cart:
                order = _create_order_from_cart(request.user, payment_method='COD', payment_status='Pending')
                CartItems.objects.filter(cart__customer=request.user).delete()
            else:
                variant = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
                quantity = int(request.POST.get('quantity', request.GET.get('qty', 1)) or 1)
                order = _create_order_from_single(request.user, variant, quantity, payment_method='COD', payment_status='Pending')

            if order:
                OrderHistory.objects.create(order=order, status='Pending', note='Cash on Delivery selected')
                messages.success(request, 'Order placed with Cash on Delivery')
                return redirect('customer_order_history')

            messages.error(request, 'Could not place COD order')
            return redirect('cart' if is_cart else 'single', id=id)

        if payment_method == 'online':
            if is_cart:
                cart_items = Cart.objects.filter(customer=request.user).select_related('product')
                total_amount = sum(item.product.selling_price * item.quantity for item in cart_items)
            else:
                variant = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
                quantity = int(request.POST.get('quantity', request.GET.get('qty', 1)) or 1)
                total_amount = variant.selling_price * quantity

            if total_amount <= 0:
                messages.error(request, 'Invalid amount for online payment')
                return redirect('cart' if is_cart else 'single', id=id)

            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = razorpay_client.order.create({
                'amount': int(total_amount * 100),
                'currency': 'INR',
                'receipt': f'rcpt_{uuid.uuid4().hex[:8]}',
                'payment_capture': 1,
            })

            context = {
                'is_cart': is_cart,
                'address': address,
                'razorpay_order': razorpay_order,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'total_amount': total_amount,
                'quantity': quantity if not is_cart else sum(item.quantity for item in cart_items),
                'product': None if is_cart else variant,
            }
            return render(request, 'customer/payment.html', context)

        messages.error(request, 'Please select a valid payment method')
        return redirect('cart' if is_cart else 'single', id=id)

    if not is_cart:
        product = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
        quantity = int(request.GET.get('qty', 1))
        subtotal = product.selling_price * quantity

        context = {
            'is_cart': False,
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
            'selling_price': product.selling_price,
            'address': address,
        }

    else:
        cart_items = Cart.objects.filter(customer=request.user).select_related('product')
        subtotal = 0
        total_quantity = 0

        for item in cart_items:
            subtotal += item.product.selling_price * item.quantity
            total_quantity += item.quantity

        context = {
            'is_cart': True,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total_quantity': total_quantity,
            'address': address,
        }

    return render(request, 'customer/payment.html', context)
@login_required(login_url="/login")
def place_cart_order(request):

    cart = Cart.objects.get(customer=request.user)
    cart_items = cart.items.all() 

    if not cart_items.exists():
        messages.error(request, "Cart is empty")
        return redirect('cart')

    for item in cart_items:
        Order.objects.create(
            user=request.user,
            product=item.product, 
            quantity=item.quantity,
            total_amount=item.product.selling_price * item.quantity
        )

    cart_items.delete()  # clear cart

    return redirect('customer_order_history')


@csrf_exempt
def razorpay_verify(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    razorpay_order_id = payload.get('razorpay_order_id')
    razorpay_payment_id = payload.get('razorpay_payment_id')
    razorpay_signature = payload.get('razorpay_signature')

    if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
        return JsonResponse({'status': 'error', 'message': 'Missing Razorpay fields'}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'status': 'failed', 'message': 'Signature mismatch'}, status=400)

    # Create order and order items after successful payment
    # This path requires order details persisted in session or note; for simplicity, mark a generic record.
    order = _create_order_from_cart(request.user, payment_method='Online', payment_status='Paid')
    if not order:
        return JsonResponse({'status': 'error', 'message': 'Unable to create order after payment'}, status=500)

    CartItems.objects.filter(cart__customer=request.user).delete()
    OrderHistory.objects.create(order=order, status='Confirmed', note='Paid through Razorpay')

    return JsonResponse({'status': 'success', 'order_number': order.order_number})


def search_view(request):
    search_product=request.GET.get('search')
    if search_product:
        product=ProductVariant.objects.filter(
            Q(product__name__icontains=search_product) | 
            Q(product__description__icontains=search_product)
        ).select_related('product').prefetch_related('images')
    else:
        product=ProductVariant.objects.none()
    return render(request,'customer/search_result.html',{'product':product, 'query': search_product})
@login_required(login_url="/login")
def review_view(request, id):
    variant = get_object_or_404(ProductVariant, id=id)
    product = variant.product
    product_reviews = Review.objects.filter(product=product).prefetch_related('images')
    if request.method == "POST":
        rating = int(request.POST.get('rating') or 0)
        comments = request.POST.get('comments', '')
        images = request.FILES.getlist('images')
        review = Review.objects.create(product=product, user=request.user, rating=rating, comments=comments)
        for img in images:
            ReviewImage.objects.create(review=review, image=img)
        return redirect('single', id=variant.id)

    in_wishlist = False
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(customer=request.user).first()
        if wishlist:
            in_wishlist = WishlistItems.objects.filter(
                wishlist=wishlist, product=variant
            ).exists()
    
    context = {
        'product': variant,
        'reviews': product_reviews,
        'user': request.user,
        'in_wishlist': in_wishlist
    }

    return render(request, 'core/single_product.html', context)




@login_required(login_url="/login")
@receiver(user_logged_in)
def register_mail(sender, request, user, **kwargs):
    subject = "Welcome to EasyPick 🎉"

    message = f"""
    Hi {user.username},

    Welcome to EasyPick! 🎉

    Your account has been successfully created.

    You can now:
    - Browse products 🛍️
    - Add items to cart 🛒
    - Place orders 🚀

    If you have any questions, feel free to contact us.

    Happy Shopping!

    Regards,  
    EasyPick Team
    """

    send_mail(
            subject,
            message,
            'dhanushasuresh2026@gmail.com',
            [user.email],
            fail_silently=False,
        )
    
def all_category(request):
    category=Category.objects.all()
    return render(request,'core/all_category.html',{"catgeory":category})

@login_required(login_url="/login")
def place_single_order(request,id):
   product = get_object_or_404(ProductVariant.objects.select_related('product').prefetch_related('images'), id=id)
   order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
   try:
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        quantity = 1
   except (ValueError, TypeError):
    quantity = 1
   total_amount = product.selling_price * quantity
   order = Order.objects.create(
        customer=request.user,
        order_number=order_number,
        total_amount=total_amount,
        payment_method='COD',
        payment_status='Pending'
    )
   OrderItem.objects.create(
        order=order,
        product=product.product,
        quantity=quantity,
        price=product.selling_price
    )
   OrderHistory.objects.create(
        order=order,
        status='Pending',
        note='Order placed successfully'
    )
   return redirect('customer_order_history')
   

@login_required(login_url="/login")
def add_wishlist_to_cart(request):

    wishlist_items = WishlistItems.objects.filter(wishlist__customer=request.user)

    cart, created = Cart.objects.get_or_create(customer=request.user)

    for item in wishlist_items:

        variant = item.product.product

        try:
            cart_item = CartItems.objects.get(cart=cart, product=variant)
            cart_item.quantity += 1
            cart_item.save()

        except CartItems.DoesNotExist:
            CartItems.objects.create(
                cart=cart,
                product=variant,
                quantity=1
            )

    return redirect('cart')

@login_required(login_url="/login")
def notification_view(request):
    notifications = request.user.core_notifications.all().order_by('-created_at')

    notifications.update(is_read=True)

    return render(request, 'customer/notifications.html', {
        'notifications': notifications
    })

@login_required(login_url="/login")
def delete_notification(request, id):
    notification = Notification.objects.get(id=id, user=request.user)
    notification.delete()
    return redirect('notifications')



