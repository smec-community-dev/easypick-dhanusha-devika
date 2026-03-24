from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import *
from seller.models import *
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()


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


# def login_view(request):
#     if request.method=="POST":
#         email=request.POST.get('email')
#         password=request.POST.get('password')
#         user=authenticate(request,password=password,username=email)
#         if user is not None:
#             login(request,user)
#             messages.success(request,'Login Successfully')
#             return redirect('home')
#         else:
#             messages.error(request,"invalid email  or password")
#             return redirect('login')
#     return render(request,'core/login.html')

@login_required
def home_view(request):
    return render(request,'core/home.html',{'data':request.user})


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

def cart_view(request):
    return render(request,'customer/cart.html')

def wishlist_view(request):
    return render(request,'customer/wishlist.html')

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
    return render(request,'shop.html')

def delete_account(request):
    if request.method=="POST":
        user=User
        password=request.POST.get('password_confirm')
        
            

    return render(request,'core/account_deletion_confirmation.html')

def delete_account_confirmation(request):
    user=request.user
    user.delete()
    messages.success(request,'deleted account')
    return redirect('/')