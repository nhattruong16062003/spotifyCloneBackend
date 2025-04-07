from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.ArtistRegistrationService import ArtistRegistrationService
from api.permissions import IsAdmin
from models.artist_registration import ArtistRegistration

class ArtistRegistrationView(APIView):
    # Permisstion để check xem người truy cập đến tất cả api trong này đã đăng nhập chưa và có phải là admin không
    permission_classes = [IsAdmin]
    """
    API endpoint để lấy tất cả yêu cầu đăng ký nghệ sĩ.
    """

    def post(self, request, action, id):
        """Xử lý approve/reject dựa trên action và id từ URL"""
        try:
            artist = ArtistRegistration.objects.get(id=id)

            if action == "artist-approve":
                result = ArtistRegistrationService.approve_artist(artist)
                return Response(result, status=status.HTTP_200_OK)
            elif action == "artist-reject":
                result = ArtistRegistrationService.reject_artist(artist)
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        except ArtistRegistration.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)


    def get(self, request, *args, **kwargs):
        # Lấy tất cả các yêu cầu đăng ký nghệ sĩ
        requests = ArtistRegistration.objects.all()
        # Sử dụng serializer để chuyển đổi dữ liệu thành JSON
        from api.serializers.ArtistRegistrationSerializer import ArtistRegistrationSerializer
        serializer = ArtistRegistrationSerializer(requests, many=True)
        # Trả về phản hồi với dữ liệu đã serialize
        return Response(serializer.data, status=status.HTTP_200_OK)
