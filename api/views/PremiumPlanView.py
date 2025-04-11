from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from models.premium_plan import PremiumPlan
from api.serializers.PremiumPlanSerializer import PremiumPlanSerializer

class PremiumPlanPagination(PageNumberPagination):
    page_size = 1  # Mặc định nếu FE không gửi page_size
    page_size_query_param = "page_size"
    max_page_size = 20

class PremiumPlanView(APIView):
    def get(self, request):
        """
        Lấy danh sách các Premium Plan (có phân trang).
        """
        try:
            plans = PremiumPlan.objects.all().order_by("id")
            paginator = PremiumPlanPagination()
            result_page = paginator.paginate_queryset(plans, request)
            serializer = PremiumPlanSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response(
                {"message_code": "PLAN_FETCH_FAILED", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Tạo mới Premium Plan.
        """
        serializer = PremiumPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id=None):
        """
        Cập nhật Premium Plan theo ID.
        """
        try:
            premium_plan = PremiumPlan.objects.get(id=id)
        except PremiumPlan.DoesNotExist:
            return Response({'detail': 'Premium plan not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PremiumPlanSerializer(premium_plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        """
        Xoá Premium Plan nếu không có ai đang sử dụng.
        """
        try:
            premium_plan = PremiumPlan.objects.get(id=id)
        except PremiumPlan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)

        if premium_plan.premiumsubscription_set.exists():
            return Response(
                {"detail": "Không thể xoá vì có người đang dùng plan này."},
                status=status.HTTP_400_BAD_REQUEST
            )

        premium_plan.delete()
        return Response({"detail": "Đã xoá plan thành công."}, status=status.HTTP_204_NO_CONTENT)
