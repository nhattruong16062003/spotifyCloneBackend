from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.ArtistRegistrationService import ArtistRegistrationService
from api.permissions import IsAdmin
from models.artist_registration import ArtistRegistration
from rest_framework.pagination import PageNumberPagination
from api.serializers.ArtistRegistrationSerializer import ArtistRegistrationSerializer

class ArtistRegistrationView(APIView):
    # Permisstion để check xem người truy cập đến tất cả api trong này đã đăng nhập chưa và có phải là admin không
    # permission_classes = [IsAdmin]
    """
    API endpoint để lấy tất cả yêu cầu đăng ký nghệ sĩ.
    """
    def post(self, request, action, id):
        """Xử lý approve/reject dựa trên action và id từ URL"""
        try:
            if action == "artist-approve":
                return ArtistRegistrationService.approve_artist(id)  
            elif action == "artist-reject":
                return ArtistRegistrationService.reject_artist(id) 
            else:
                return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        except ArtistRegistration.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)


    # def get(self, request, *args, **kwargs):
    #     # Lấy tất cả các yêu cầu đăng ký nghệ sĩ
    #     requests = ArtistRegistration.objects.all()
    #     # Sử dụng serializer để chuyển đổi dữ liệu thành JSON
    #     serializer = ArtistRegistrationSerializer(requests, many=True)
    #     # Trả về phản hồi với dữ liệu đã serialize
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     requests = ArtistRegistration.objects.all().order_by('-created_at')

    #     paginator = ArtistRegistrationPagination()
    #     result_page = paginator.paginate_queryset(requests, request)
    #     serializer = ArtistRegistrationSerializer(result_page, many=True)
    #     return paginator.get_paginated_response(serializer.data)



    def get(self, request, page):
        #Lấy toàn bộ dữ liệu 
        requests = ArtistRegistration.objects.all().order_by('-created_at')

        #Gán page từ URL vào request.GET['page'] → để paginator có thể đọc:
        request.GET._mutable = True
        request.GET['page'] = page
        request.GET._mutable = False

        paginator = ArtistRegistrationPagination()
        result_page = paginator.paginate_queryset(requests, request)
        serializer = ArtistRegistrationSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    
class ArtistRegistrationPagination(PageNumberPagination):
    page_size = 3  # Số bản ghi mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 100