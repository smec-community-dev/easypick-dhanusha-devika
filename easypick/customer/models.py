from django.db import models
from core.models import *
from seller.models import *
from django.conf import settings
User = settings.AUTH_USER_MODEL

# Create your models here.
class Cart(models.Model):

    cart_id = models.AutoField(primary_key=True)

    customer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.customer}"

class CartItems(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        'seller.ProductVariant',
        on_delete=models.CASCADE,
        related_name="item"
    )

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class Wishlist(models.Model):

    wishlist_id = models.AutoField(primary_key=True)

    customer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    created_at = models.DateTimeField(auto_now_add=True,null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist - {self.customer}"

class WishlistItems(models.Model):

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        'seller.ProductVariant',
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name}"

class Order(models.Model):

    order_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_number = models.CharField(max_length=50, unique=True)

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    PAYMENT_METHOD = (
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD
    )

    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number
    
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        'seller.Product',
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.product}"
    
class Review(models.Model):

    review_id = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        'seller.Product',
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name="user_reviews"
    )

    rating = models.PositiveIntegerField()

    comments = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.user} - {self.product} - {self.rating}"
    
class ReviewImage(models.Model):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to='review_images/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Review {self.review.review_id}"
    
class OrderHistory(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="history"
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES
    )

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
    
class OrderNotification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_notifications'
    )

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.title}"