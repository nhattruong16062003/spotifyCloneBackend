from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from services.UserService import UserService

class UserView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        user = UserService.get_user_by_id(user_id)
        if user is not None:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'google_id': user.google_id,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at,
                'premium_start': user.premium_start,
                'premium_end': user.premium_end,
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)