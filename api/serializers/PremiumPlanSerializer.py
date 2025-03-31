from rest_framework import serializers
from models.premium_plan import PremiumPlan 

class PremiumPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPlan
        fields = ["id", "name", "price", "duration_days"]
