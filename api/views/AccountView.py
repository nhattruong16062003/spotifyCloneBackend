import uuid
import boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from api.serializers.UserSerializer import UserSerializer
from services.UploadService import UploadService
from PIL import Image
from io import BytesIO


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Lấy thông tin người dùng hiện tại.
        """
        user = request.user
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Cập nhật thông tin người dùng hiện tại.
        """
        # Parse the incoming data
        data = request.data
        user = request.user  # Lấy thông tin người dùng hiện tại

        # Check for uploaded file in request.FILES
        image_url = None
        if "image_path" in request.FILES:
            image = request.FILES["image_path"]
            original_image_name = image.name  # Lưu tên gốc của file

            # Kiểm tra và chuyển đổi chế độ màu nếu cần
            try:
                img = Image.open(image)
                if img.mode == "RGBA":
                    img = img.convert("RGB")  # Chuyển đổi sang chế độ RGB
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    buffer.seek(0)
                    image = buffer  # Thay thế file gốc bằng file đã chuyển đổi
            except Exception as e:
                return Response(
                    {"message_code": "IMAGE_PROCESSING_FAILED", "details": str(e)},
                    status=500,
                )

            image_name = f"images/{original_image_name}"  # Sử dụng tên gốc của file
            image_url = UploadService.upload_image_to_s3(image, image_name)
            if not image_url:
                return Response({"message_code": "IMAGE_UPLOAD_FAILED"}, status=500)
        else:
            # Nếu không có ảnh mới, giữ nguyên ảnh hiện tại
            image_url = user.image_path

        # Cập nhật thông tin người dùng
        user.username = data.get("username", user.username)
        user.image_path = image_url  # Giữ nguyên hoặc cập nhật ảnh mới nếu có

        # Lưu thay đổi
        try:
            user.save()
        except Exception as e:
            # Nếu lưu thất bại, xóa ảnh đã upload lên S3 (nếu có)
            if image_url and "image_path" in request.FILES:
                UploadService.delete_image_from_s3(image_name)
            return Response(
                {"message_code": "USER_UPDATE_FAILED", "details": str(e)}, status=500
            )

        return Response({"message_code": "USER_UPDATE_SUCCESS"}, status=status.HTTP_200_OK)