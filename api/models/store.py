from django.db import models


class Store(models.Model):
    store_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.name