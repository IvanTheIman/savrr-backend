from django.db import models


class Product(models.Model):
    """
    Model for product that includes, product id, name, unit, image, and barcode which is optional
    """
    product_id = models.CharField(max_length=50)
    name = models.CharField(max_length=80)
    unit = models.CharField(max_length=20)
    image = models.ImageField(upload_to='product/', null=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True, db_index=True)

    def __str__(self):
        return self.name
    
    def get_price(self, store):
        from .price import PriceHistory
        latest_price = PriceHistory.objects.filter(
            product=self, 
            store=store
        ).order_by('-date').first()
        return latest_price.price if latest_price else None


class ProductBarcode(models.Model):
    """
    Model for product barcode that includes, product, barcode, source, variant name, and date added at
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='barcodes')
    barcode = models.CharField(max_length=100, unique=True, db_index=True)
    source = models.CharField(max_length=50, blank=True, null=True)
    variant_name = models.CharField(max_length=100, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Barcode'
        verbose_name_plural = 'Product Barcodes'
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.barcode} → {self.product.name}"