from django.db import models
from django.conf import settings

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Laptop(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    cpu = models.CharField(max_length=100)
    ram = models.IntegerField()
    storage = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.laptop.name}"

    def subtotal(self):
        return self.laptop.price * self.quantity