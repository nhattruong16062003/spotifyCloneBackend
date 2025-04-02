from rest_framework import serializers
from models.user import User  # Correct the import path
import re  # Thêm dòng này vào đầu file để sử dụng module re



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #Serializer giúp chuyển đổi từ object đưới databse -> json để gửi lên client 
        #SSerializer giúp chuyển đổi json từ client xuống backend để lưu vào database
        #Serializer giúp validate dữ liệu đầu vào 

        #Định nghĩa các trước của module user sẽ được sử dụng trong serializer, có nghĩa là sẽ chuyển đổi những trường nào. 
        fields = ['name', 'email', 'password','image_path']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    #-------------Custom hàm để kiểm tra kiểm tra dữ liệu đầu vào---------------------------#
    #-------------mặc định django có cơ chế giúp kiểm tra các trướng dữ liệu dựa vào databse#

  