from django.db import models


class PriceHistory(models.Model):
    product = models.ForeignKey('api.Product', on_delete=models.CASCADE)
    store = models.ForeignKey('api.Store', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Price Histories'
        indexes = [
            models.Index(fields=['product', 'store', '-date']),
        ]

    def __str__(self):
        return f"{self.product.name} at {self.store.name} on {self.date}: ${self.price}"