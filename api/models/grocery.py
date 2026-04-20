from django.db import models
from grocery_backend import settings


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
        'api.Product',
        on_delete=models.CASCADE,
        related_name='grocery_items'
    )
    store = models.ForeignKey('api.Store', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_checked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('grocery_list', 'product', 'store')

    def __str__(self):
        store_name = self.store.name if self.store else "No Store"
        return f"{self.quantity}x {self.product.name} @ {store_name}"

    @property
    def subtotal(self):
        if not self.store:
            return None
        price = self.product.get_price(self.store)
        return price * self.quantity if price else None