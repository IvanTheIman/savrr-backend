
from django.db import models
from django.contrib.auth.models import AbstractUser
from grocery_backend import settings


class User(AbstractUser):
    """
    model for user(general)
    """
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    model for user profile which includes the user, and dat created, and future attributes such 
    as avatar and bio 
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class UserLocation(models.Model):
    """
    model for user location that includes the user, their latittude and longitude and date created
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} @ ({self.latitude}, {self.longitude})"