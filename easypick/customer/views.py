from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from core.models import *
from seller.models import *
from customer.models import *
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Q, Avg
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
import random




# Create your views here.
def customer_register_view(request):
    if request.method=="POST":
        
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")
        if password != confirm_password:
            messages.error(request,'password do not match')
            return redirect('customer_register')
        if User.objects.filter(email=email).exists():
            messages.error(request,'email already exists')
            return redirect('customer_register')
        user = User.objects.create_user( username=email,email=email, password=password, first_name=first_name, last_name=last_name )
        messages.success(request, "Account created successfully")
        return redirect('login')
    return render(request,'core/customer_registartion.html')

@login_required
def home_view(request):
    products=ProductVariant.objects.all()
    cart_item=CartItems.objects.filter(cart__customer=request.user)
    wishlist_item=WishlistItems.objects.filter(wishlist__customer=request.user)
    category=Category.objects.all()

    return render(request,'core/home.html',{'data':request.user,'category':category,"products":products,"cart_item":cart_item,"wishlist_item":wishlist_item})

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

def customer_order_history(request):
    return render(request,'customer/customer_orderdeatils.html')

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

def subcategory_view(request,id):
    product=ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
    return render(request,'core/subcategory.html',{'product':product})

def single_view(request, id):
  
    product = get_object_or_404(ProductVariant.objects.select_related('product').prefetch_related('images'),id=id)

    if request.method == "POST":
        if request.user.is_authenticated:
            comment = request.POST.get('comment', '').strip()
            rating_str = request.POST.get('rating', '5')
            
            try:
                rating = int(rating_str)
                if 1 <= rating <= 5:
                    Review.objects.create(
                        product=product.product,
                        user=request.user,
                        comments=comment,
                        rating=rating
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


    return render(request, 'core/single_product.html', {'product': product,'reviews': reviews,'in_wishlist': in_wishlist,'related_products':related_products,})

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
    cart_item = CartItems.objects.filter(cart=cart_user).select_related('product')
        
   
    subtotal = Decimal('0')
    for item in cart_item:
        subtotal += (item.product.selling_price * item.quantity)
    return render(request,'customer/cart.html',{'cart_item':cart_item, 'subtotal': subtotal,'cart':cart})   
   
@login_required
def cart_order(request,id):
    # cart=Cart.objects.get(customer=request.user)
    # cart_item=CartItems.objects.filter(cart=cart).select_related('product')
    cart_item=CartItems.objects.filter(cart__customer=request.user).select_related('product')
    address=Address.objects.filter(user=request.user).first()
    subtotal=0
    for item in cart_item:
        subtotal += item.product.selling_price * item.quantity
        total=subtotal+5
            
    addresses = Address.objects.filter(user=request.user)
    return render(request,'customer/cart_orderconfirm.html',{'cart_item':cart_item,'address':address,'addresses':addresses,'subtotal':subtotal,"total":total})

@login_required(login_url="/login")
def order_confirm_view(request, id):
    product = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
    address = Address.objects.filter(user=request.user)
    
    quantity = request.GET.get('qty', 1)
    quantity = int(quantity)
    
    selling_price = product.selling_price
    subtotal = selling_price * quantity
    
    
    
    context = {
        'product': product,
        'address': address,
        'quantity': quantity,
        'subtotal': subtotal,
        'selling_price': selling_price,
    }
    return render(request, 'customer/order_confirm.html', context)
@login_required(login_url="/login")
def payment_view(request):
    cart_item=CartItems.objects.filter(cart__customer=request.user).select_related('product')
    subtotal=0
    for item in cart_item:
        subtotal += item.product.selling_price * item.quantity
            
    return render(request,'customer/payment.html',{"subtotal":subtotal})

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
# @login_required(login_url="/login")
# def review_view(request, id):
#     variant = get_object_or_404(ProductVariant, id=id)
#     product = variant.product
#     product_reviews = Review.objects.filter(product=product).prefetch_related('images')
#     if request.method == "POST":
#         rating = int(request.POST.get('rating') or 0)
#         comments = request.POST.get('comments', '')
#         images = request.FILES.getlist('images')
#         review = Review.objects.create(product=product, user=request.user, rating=rating, comments=comments)
#         for img in images:
#             ReviewImage.objects.create(review=review, image=img)
#         return redirect('single', id=variant.id)

#     in_wishlist = False
#     if request.user.is_authenticated:
#         wishlist = Wishlist.objects.filter(customer=request.user).first()
#         if wishlist:
#             in_wishlist = WishlistItems.objects.filter(
#                 wishlist=wishlist, product=variant
#             ).exists()
    
#     context = {
#         'product': variant,
#         'reviews': product_reviews,
#         'user': request.user,
#         'in_wishlist': in_wishlist
#     }

#     return render(request, 'core/single_product.html', context)




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
def place_order(request):

    
    cart_items = CartItems.objects.filter(cart__customer=request.user)

    total = 0

   
    order_number = f"ORD{random.randint(1000,9999)}"

    
    order = Order.objects.create(
        customer=request.user,
        order_number=order_number,
        total_amount=0,
        payment_method='COD',   
        payment_status='Pending'
    )

    
    for item in cart_items:
        variant = item.product
        product = variant.product
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            price=variant.selling_price
        )

        total += variant.selling_price * item.quantity

   
    order.total_amount = total
    order.save()

    
    cart_items.delete()
    print("hlooo")

    return redirect('payment')

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