from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import UserLocation

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration which includes a function to create a new user
    """
    first_name = serializers.CharField(required=True) 
    last_name = serializers.CharField(required=True)  
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name'] 
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),  
            last_name=validated_data.get('last_name', ''),    
        )
        return user
    
class UserLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for user location
    """
    class Meta:
        model = UserLocation
        fields = "__all__"
