from django.db import models
from core.models import *

# Create your models here.
class SellerProfile(models.Model):
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=255)
    store_slug = models.SlugField(unique=True)
    gst_number = models.CharField(max_length=50)
    pan_number = models.CharField(max_length=50)
    bank_account_number = models.CharField(max_length=50,null=True)
    ifsc_code = models.CharField(max_length=20,null=True)
    business_address = models.TextField(null=True)
    rating = models.FloatField(default=0,null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")




class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    is_cancellable = models.BooleanField(default=True)
    is_returnable = models.BooleanField(default=True)
    return_days = models.IntegerField(default=7)
    approval_status = models.CharField(max_length=20, default='PENDING')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku_code = models.CharField(max_length=100, unique=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    weight = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    tax_percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product}'s variant"
    
    @property
    def get_discount_percentage(self):
        if self.mrp and self.selling_price and self.mrp > 0:
            discount = ((self.mrp - self.selling_price) / self.mrp) * 100
            return discount
        return 0

class ProductImage(models.Model): 
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="images") 
    image = models.ImageField(upload_to='product_image') 
    alt_text = models.CharField(max_length=255, blank=True) 
    is_primary = models.BooleanField(default=False) 
    def __str__(self): return F"{self.variant}'s image "

class Attribute(models.Model):
    name = models.CharField(max_length=100)

class AttributeOption(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=100)

class VariantAttributeBridge(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    option = models.ForeignKey(AttributeOption, on_delete=models.CASCADE)
class InventoryLog(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='logs'   
    )
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# class Discount(models.Model):
#     product = models.ForeignKey('seller.Product',on_delete=models.CASCADE,related_name='discounts')
#     code = models.CharField(max_length=50, unique=True, null=True, blank=True)
#     discount_value = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_type = models.CharField(max_length=20)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     usage_limit = models.IntegerField(default=1)
#     used_count = models.IntegerField(default=0)
#     min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     max_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     status = models.CharField(max_length=20,default='scheduled')
#     created_at = models.DateTimeField(auto_now_add=True)
