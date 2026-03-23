from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from seller.models import ProductVariant

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
def shop_view(request):
    return render(request,'core/shop.html')
def logout_view(request):
    logout(request)
    messages.success(request,"Logout")
    return redirect("mainhome")


def main_home(request):
    clothing_products = ProductVariant.objects.filter(
        product__status="APPROVED",
        product__subcategory__subcategory_name__in=["Shirt", "Jeans", "watch","Shoes","Sandals","Hoodies","TShirt","Top"]
    )

    electronics_products = ProductVariant.objects.filter(
        product__status="APPROVED",
        product__subcategory__subcategory_name__in=[
            "Laptop", "TV", "Mobile Phone", "Radio","AC","Camera","Headphones"
        ]
    ).distinct()

    home_appliances_products = ProductVariant.objects.filter(
        product__status="APPROVED",
        product__subcategory__subcategory_name__in=[
            "Mixer Grinder","Oven","Washing Machine","Fridge"
        ]
    )

    context = {
        "clothing_products": clothing_products,
        "electronics_products": electronics_products,
        "home_appliances_products": home_appliances_products, 
    }

    return render(request, "core/mainhome.html", context)

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
            return redirect('mainhome')
    return render(request,'admin/admin_login.html')