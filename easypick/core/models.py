from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('SELLER', 'Seller'),
        ('CUSTOMER', 'Customer'),)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='CUSTOMER'  
    )
    phone_number=models.CharField(max_length=11,null=True)
    address=models.CharField(max_length=100,null=True)
    profile_image=models.ImageField(upload_to='profile_image',null=True,blank=True)
    gender=models.CharField(max_length=10,null=True)
    age=models.IntegerField(null=True)
    dob=models.DateField(null=True,blank=True)
    date_login=models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='addresses')
    full_name=models.CharField(max_length=100,null=True)
    phone_number=models.CharField(max_length=15,null=True)
    house_no=models.CharField(max_length=100,null=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    landmark=models.CharField(max_length=100,null=True)
    address_type=models.CharField(max_length=12,null=True)
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='core_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    customer_id=models.ForeignKey(User,on_delete=models.CASCADE)
    category_name=models.CharField(max_length=20) 
    category_description=models.CharField(max_length=200)
    category_image=models.ImageField(upload_to='category/',null=True,blank=True)
    created_at=models.DateField()
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)

class SubCategory(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,)
    subcategory_name = models.CharField(max_length=50)
    subcategory_description = models.CharField(max_length=200)
    subcategory_image = models.ImageField(upload_to='subcategory/',null=True,blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)