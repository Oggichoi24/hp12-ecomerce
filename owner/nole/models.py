from django.db import models
from django.conf import settings


class Laptop(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    cpu = models.CharField(max_length=100)
    ram = models.IntegerField()
    storage = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    laptop = models.ForeignKey(
        Laptop,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.laptop.name}"

    def subtotal(self):
        return self.laptop.price * self.quantity


# =========================
# ORDER MODELS
# =========================

class Order(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPING', 'Shipping'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def calculate_total(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.total_price = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    laptop = models.ForeignKey(
        Laptop,
        on_delete=models.SET_NULL,
        null=True
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.quantity} x {self.laptop}"

    def subtotal(self):
        return self.price * self.quantity