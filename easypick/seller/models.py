from django.db import models
from core.models import *
from django.utils import timezone
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

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

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
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)

    
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
        return f"{self.product.name} - {self.sku_code}"

class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)




class Attribute(models.Model):
    name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

class AttributeOption(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=100)

class VariantAttributeBridge(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    option = models.ForeignKey(AttributeOption, on_delete=models.CASCADE)

class InventoryLog(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE,related_name="logs")
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Discount(models.Model):
    variant = models.ForeignKey(
    ProductVariant,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="discounts"
)

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    discount_percent = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    