from rest_framework import serializers
from models.user import User  # Correct the import path

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password','image_path']
        # fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            is_active=False  # Set is_active to False initially
        )
        user.set_password(validated_data['password'])
        user.save()
        return user