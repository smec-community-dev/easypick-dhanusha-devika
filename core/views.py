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
from .decorators import role_required
import random
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta
from .models import PasswordResetOTP

from django.shortcuts import render, redirect
from django.utils.timezone import now
from datetime import timedelta
from .models import PasswordResetOTP
from django.utils.timezone import now
from datetime import timedelta


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser or user.role == "ADMIN":
                return redirect("admin_dashboard")

            elif user.role == "SELLER":
                return redirect("seller_dashboard")

            elif user.role == "CUSTOMER":
                return redirect("home")

            return redirect("home")

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "core/login.html")

@role_required(allowed_roles=["ADMIN"])
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




def logout_view(request):
    logout(request)
    messages.success(request,"Logout")
    return redirect("/")
@role_required(allowed_roles=["SELLER"])
def about_view(request):
    return render(request,'core/about.html')

def contact_view(request):
    return render(request,'core/contact.html')


import random
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP

User = get_user_model()
import random
from django.core.mail import send_mail

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)

            otp = str(random.randint(100000, 999999))
            print("Generated OTP:", otp)

            PasswordResetOTP.objects.create(
                user=user,
                otp=otp
            )

            # ✅ VERY IMPORTANT
            request.session['reset_user'] = user.id

            # send email
            send_mail(
                'Your OTP',
                f'Your OTP is {otp}',
                'dhanushasuresh2026@gmail.com',
                [user.email],
                fail_silently=False,
            )

            return redirect('core_verify_otp')

        except User.DoesNotExist:
            return render(request, 'core/forgot_password.html', {'error': 'User not found'})

    return render(request, 'core/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('reset_user')

        records = PasswordResetOTP.objects.filter(user_id=user_id)
        record = records.filter(otp=otp).last()

        if record and now() - record.created_at < timedelta(minutes=5):
            return redirect('set_new_password')
        else:
            return render(request, 'core/verify_otp.html', {'error': 'Invalid or Expired OTP'})

    return render(request, 'core/verify_otp.html')

def set_new_password(request):
    if request.method == 'POST':
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')

        user_id = request.session.get('reset_user')

        if not user_id:
            return redirect('forgot_password')

        if p1 == p2:
            user = User.objects.get(id=user_id)
            user.set_password(p1)
            user.save()

            request.session.flush()

            return redirect('login')
        else:
            return render(request, 'core/set_new_password.html', {'error': 'Passwords do not match'})

    return render(request, 'core/set_new_password.html')