from django.db import models
from django.contrib.auth.models import AbstractUser

from grocery_backend import settings

class Store(models.Model):
    store_id = models.CharField(max_length = 50)
    name = models.CharField(max_length = 50)
    location = models.CharField(max_length = 50)
    latitude = models.FloatField(null = True, blank = True)
    longitude = models.FloatField(null = True, blank = True)
    
   
    def __str__(self):
        return self.name 
    
class Product(models.Model):
    product_id = models.CharField(max_length = 50)
    name = models.CharField(max_length = 80)
    unit = models.CharField(max_length = 20)
    image = models.ImageField(upload_to = 'product/', null = True, blank = True)

    def __str__ (self):
        return self.name
    
    def get_price(self, store):
        latest_price = PriceHistory.objects.filter(
            product = self, 
            store = store
        ).order_by('-date').first()
        return latest_price.price if latest_price else None

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    store = models.ForeignKey(Store, on_delete = models.CASCADE)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    date = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Price Histories'
        indexes = [
            models.Index(fields=['product', 'store', '-date']),
        ]

    def __call__(self):
        return f"{self.product.name} at {self.store.name} on {self.date}: ${self.price}"

    
class User(AbstractUser):
    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    avatar = models.ImageField(upload_to = 'avatars/', blank = True, null = True)
    bio = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class UserLocation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'locations'
    )
    latitude = models.FloatField(null = True, blank = True)
    longitude = models.FloatField(null = True, blank = True)
    created_at = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.username} @ ({self.latitude}, {self.longitude})"
    
class GroceryList(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grocery_lists'
    )
    name = models.CharField(max_length=100, default='My Grocery List')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username} — {self.name}"



class GroceryItem(models.Model):
    grocery_list = models.ForeignKey(
        GroceryList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='grocery_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    is_checked = models.BooleanField(default=False)  # user ticks off as they shop

    class Meta:
        unique_together = ('grocery_list', 'product')  # no duplicate products in same list

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        price = self.product.get_price(self.grocery_list.store)
        return price * self.quantity if price else None

