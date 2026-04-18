# api/serializers/user_serializer.py

from rest_framework import serializers
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)  # ADD
    last_name = serializers.CharField(required=True)   # ADD
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']  # ADD first_name, last_name
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),  # ADD
            last_name=validated_data.get('last_name', ''),    # ADD
        )
        return user