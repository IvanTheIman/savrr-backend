from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from api.models import User, UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone')

    def create(self, validated_data):
        # Use create_user so password is hashed, never stored plain
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'avatar', 'bio', 'created_at')