from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from core.models import *
from core.models import Category

# Create your views here.
def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')
    return render(request, 'admin/admin_dashboard.html')

def user_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')
    total_user=User.objects.count()
    active=User.objects.filter(is_active=True).count()
    users=User.objects.all()
    return render(request,'admin/admin_user.html',{"count":total_user,"active":active,"user":users})



def admin_category(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You are not authorized as admin")
        return redirect('admin_login')
    categories = Category.objects.prefetch_related('subcategory_set').all()
    return render(request, 'admin/admin_category.html', {'categories': categories})

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
    
    return render(request, 'admin/add_category.html', {'categories': categories})
