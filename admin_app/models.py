from django.db import models
from seller.models import *
from core.models import *
from customer.models import *

# Create your models here.
class Offer(models.Model):
    offer_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percentage = models.DecimalField(max_digits=5,decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    per_user_limit = models.IntegerField(default=1)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
