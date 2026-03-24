from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from seller.models import ProductVariant
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # log the user in

            # Admin / superuser
            if user.is_superuser or user.role == "ADMIN":
                return redirect("admin_dashboard")

            # Seller → dashboard view will handle pending check
            elif user.role == "SELLER":
                return redirect("seller_dashboard")

            # Customer
            elif user.role == "CUSTOMER":
                return redirect("home")

            # Fallback
            messages.success(request, "Login Successfully")
            return redirect("mainhome")

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    # GET → just render login page
    return render(request, "core/login.html")

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

# def admin_view(request):
#     if request.method=="POST":
#         username=request.POST.get('email')
#         password=request.POST.get('password')
#         user=authenticate(request,password=password,username=username)
#         if user is not None and user.is_superuser:
#             login(request,user)
#             messages.success(request,'Login Successfully')
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request,"You are not authorized as admin")
#             return redirect('mainhome')
#     return render(request,'core/login.html')