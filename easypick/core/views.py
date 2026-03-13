from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from seller.models import ProductVariant
from customer.models import Wishlist, WishlistItems

def main_home_view(request):
    return render(request,'core/main_home.html')
def login_view(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=authenticate(request,password=password,username=email)
        if user is not None:
            login(request,user)
            messages.success(request,'Login Successfully')
            return redirect('home')
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
            return redirect('admin_dashboard')
        else:
            messages.error(request,"You are not authorized as admin")
            return redirect('login')
    return render(request,'admin/admin_login.html')


def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')
    return render(request, 'admin/admin_dashboard.html')


def shop_view(request):
    product = ProductVariant.objects.select_related('product').prefetch_related('images').all()
    
    sort = request.GET.get('sort', 'new_arrival')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if sort == 'low':
        product = product.order_by('selling_price')
    elif sort == 'high':
        product = product.order_by('-selling_price')
    elif sort == 'new_arrival':
        product = product.order_by('-id')
    
    if min_price:
        product = product.filter(selling_price__gte=min_price)
    if max_price:
        product = product.filter(selling_price__lte=max_price)
    
    products_count = product.count()
    product = product[:20]  # pagination limit
    
    in_wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(customer=request.user).first()
        if wishlist:
            in_wishlist_ids = set(
                WishlistItems.objects.filter(wishlist=wishlist).values_list("product_id", flat=True)
            )
    
    return render(request, 'core/shop.html', {
        'product': product,
        'products': product,  # for count
        'products_count': products_count,
        'in_wishlist_ids': in_wishlist_ids
    })

def logout_view(request):
    logout(request)
    messages.success(request,"Logout")
    return redirect("login")
