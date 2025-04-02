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
from services.AccountService import AccountService
from models.user import User
from django.shortcuts import get_object_or_404



class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Lấy thông tin người dùng hiện tại.
        """
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {"message_code": "USER_NOT_AUTHENTICATED", "details": "User is not authenticated."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_data = UserSerializer(user).data
            return Response(user_data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = str(e)
            return Response(
                {"message_code": "USER_FETCH_FAILED", "details": error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        """
        Cập nhật thông tin người dùng hiện tại.
        """
        user = request.user
        data = request.data
        files = request.FILES
        action = data.get('action')
        image_path = user.image_path 
        try:
            updated_user = AccountService.update_user(user, data, files, image_path,action)
            updated_user_data = UserSerializer(updated_user).data
            return Response(
                {"message_code": "USER_UPDATE_SUCCESS", "user": updated_user_data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message_code": "ERROR_OCCURRED", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )