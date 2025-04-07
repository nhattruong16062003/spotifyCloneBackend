from rest_framework import serializers
from models.user import User  # Correct the import path
from models.role import Role  # Import model Role
from api.serializers.RoleSerializer import RoleSerializer
import re  # Thêm dòng này vào đầu file để sử dụng module re



class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)  # Nhúng RoleSerializer vào UserSerializer
    class Meta:
        model = User
        #Serializer giúp chuyển đổi từ object đưới databse -> json để gửi lên client 
        #SSerializer giúp chuyển đổi json từ client xuống backend để lưu vào database
        #Serializer giúp validate dữ liệu đầu vào 

        #Định nghĩa các trước của module user sẽ được sử dụng trong serializer, có nghĩa là sẽ chuyển đổi những trường nào. 
        fields = ['id','name', 'email', 'password','image_path','role','is_ban']

        extra_kwargs = {
            'password': {'write_only': True}
        }


  