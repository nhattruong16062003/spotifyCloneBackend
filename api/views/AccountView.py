from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from api.serializers.UserSerializer import UserSerializer
from services.AccountService import AccountService
from models.user import User
from rest_framework.decorators import permission_classes


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, action, id):
        """
        Ban hoặc mở khóa tài khoản người dùng (set is_ban).
        """
        try:
            # Bắt đầu transaction
            with transaction.atomic():
                # Lấy đối tượng người dùng từ ID
                user_to_update = get_object_or_404(User, id=id)

                # Kiểm tra quyền của người dùng
                if not request.user.role.name == "admin":
                    return Response(
                        {"message_code": "FORBIDDEN", "details": "You do not have permission to modify users."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Gọi service để ban hoặc unban tài khoản
                message_code, message = AccountService.ban_or_unban_user(user_to_update, action)

                return Response(
                    {"message_code": message_code, "details": message, "user_id": user_to_update.id},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"message_code": "USER_UPDATE_FAILED", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def get(self, request, profile_id=None):
        if request.path.startswith('/api/public-profile/'):
            return self.get_user_by_id(request, profile_id)
        elif request.path == '/api/account/':
            return self.get_user_info(request)
        elif request.path == '/api/admin/accounts/':
            return self.get_all_users(request)
        else:
            return Response(
                {"message_code": "INVALID_ACTION", "details": "Invalid action specified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_user_info(self, request):
        """
        Lấy thông tin người dùng hiện tại.
        """
        try:
            user = request.user
            user_data = AccountService.get_user_info(user)
            return Response(user_data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = str(e)
            return Response(
                {"message_code": "USER_FETCH_FAILED", "details": error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_all_users(self, request):
        """
        Lấy tất cả người dùng (chỉ dành cho admin).
        """
        try:
            if not request.user.role.name == "admin":
                return Response(
                    {"message_code": "FORBIDDEN", "details": "You do not have permission to view all users."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_data = AccountService.get_all_users()
            return Response(user_data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = str(e)
            return Response(
                {"message_code": "USER_FETCH_FAILED", "details": error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_user_by_id(self, request, profile_id):
        """
        Lấy thông tin người dùng theo ID
        profile_id chính là id của account được truyền vào
        """
        try:
            user = get_object_or_404(User, id=profile_id)  # Lấy user từ DB
            user_data = UserSerializer(user).data  # Serialize dữ liệu
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
            # Bắt đầu transaction
            with transaction.atomic():
                updated_user = AccountService.update_user(user, data, files, image_path, action)
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
