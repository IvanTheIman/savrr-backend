from django.db import models

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
    
class UserLocation(models.Model):
    latitude = models.FloatField(null = True, blank = True)
    longitude = models.FloatField(null = True, blank = True)
    created_at = models.DateField(auto_now_add = True)
    

