from django.db import models
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False, null=False, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
