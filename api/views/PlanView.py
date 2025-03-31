from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models.models import PremiumPlan
from api.serializers.PremiumPlanSerializer import PremiumPlanSerializer

class PlanListView(APIView):
    """API lấy danh sách tất cả các gói Premium"""
    def get(self, request):
        plans = PremiumPlan.objects.all()
        serializer = PremiumPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PlanDetailView(APIView):
    """API lấy thông tin gói Premium theo ID"""
    def get(self, request, plan_id, *args, **kwargs):
        try:
            plan = PremiumPlan.objects.get(id=plan_id)
            serializer = PremiumPlanSerializer(plan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PremiumPlan.DoesNotExist:
            return Response({"message": "Gói Premium không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
