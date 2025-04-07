from rest_framework import serializers
from models.role import Role  # Giả sử bạn đã có model Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']  # Chỉ lấy các trường cần thiết
