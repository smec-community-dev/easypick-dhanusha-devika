from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.mail import send_mail
from seller.models import *
from customer.models import *
from core.models import *

def main_home_view(request):
    products=ProductVariant.objects.all().select_related('product').prefetch_related('images')
    category=Category.objects.all()
    return render(request,'core/main_home.html',{"products":products,"category":category})
def login_view(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=authenticate(request,password=password,username=email)
        if user is not None:
            # if user.role=="ADMIN":
            #     return redirect("admin_dashboard")
            # elif user.role=="SELLER":
            #     return redirect("seller_dashboard")
            # elif user.role=="CUSTOMER":
            #     return redirect("home")          
            # login(request,user)
            # messages.success(request,'Login Successfully')
            # return redirect('home')
            login(request,user)
            return redirect("home")
        else:
            messages.error(request,"invalid email  or password")
            return redirect('login')
    return render(request,'core/login.html')

def admin_view(request):
    if request.method=="POST":
        username=request.POST.get('email')
        password=request.POST.get('password')
        user=authenticate(request,password=password,username=username)
        if user is not None and user.is_superuser:
            login(request,user)
            messages.success(request,'Login Successfully')
            print(request.user)
            return redirect('admin_dashboard')

        else:
            messages.error(request,"You are not authorized as admin")
            return redirect('login')
    return render(request,'admin/admin_login.html')


# def shop_view(request):
#     product = ProductVariant.objects.select_related('product').prefetch_related('images').all()
    
#     sort = request.GET.get('sort', 'new_arrival')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
    
#     if sort == 'low':
#         product = product.order_by('selling_price')
#     elif sort == 'high':
#         product = product.order_by('-selling_price')
#     elif sort == 'new_arrival':
#         product = product.order_by('-id')
    
#     if min_price:
#         product = product.filter(selling_price__gte=min_price)
#     if max_price:
#         product = product.filter(selling_price__lte=max_price)
    
#     products_count = product.count()
#     product = product[:20]  # pagination limit
    
#     in_wishlist_ids = set()
#     if request.user.is_authenticated:
#         wishlist = Wishlist.objects.filter(customer=request.user).first()
#         if wishlist:
#             in_wishlist_ids = set(
#                 WishlistItems.objects.filter(wishlist=wishlist).values_list("product_id", flat=True)
#             )
    
#     return render(request, 'core/shop.html', {
#         'product': product,
#         'products': product,  # for count
#         'products_count': products_count,
#         'in_wishlist_ids': in_wishlist_ids
#     })

def logout_view(request):
    logout(request)
    messages.success(request,"Logout")
    return redirect("login")

def about_view(request):
    return render(request,'core/about.html')

def contact_view(request):
    return render(request,'core/contact.html')

# @receiver(user_logged_in)
# def login_mail(sender, request, user, **kwargs):
#     subject = "Login Alert - Your Account"
    
#     message = f"""
# Hi {user.username},

# You have successfully logged into your account.

# If this wasn't you, please secure your account immediately.

# Thank you,
# Your E-commerce Team
# """

#     send_mail(
#         subject,
#         message,
#         'dhanushasuresh2026@gmail.com',
#         [user.email],
#         fail_silently=False,
#     )