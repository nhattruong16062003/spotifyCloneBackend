import logging
import json
import uuid
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from models.premium_plan import PremiumPlan
from models.premium_subscription import PremiumSubscription
from .models import Transaction

logger = logging.getLogger(__name__)

class CashView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            user_id = request.user.id
            
            # Kiểm tra nếu user đã có gói Premium còn hạn
            existing_subscription = PremiumSubscription.objects.filter(
                user_id=user_id,
                end_date__gte=timezone.now()
            ).exists()
            
            if existing_subscription:
                return JsonResponse({'error': 'User already has an active premium subscription'}, status=401)

            # Lấy dữ liệu từ request
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            
            if not plan_id:
                return JsonResponse({'error': 'plan_id is required'}, status=400)
            
            try:
                plan = PremiumPlan.objects.get(id=plan_id)
            except PremiumPlan.DoesNotExist:
                return JsonResponse({'error': 'Plan not found'}, status=404)
            
            # Tạo giao dịch thành công
            txn_ref = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                txn_ref=txn_ref,
                amount=plan.price,
                payment_method="cash",
                order_info=f"Thanh toán tiền mặt cho gói {plan.name}",
                status='success'
            )

            # Cấp Premium cho user
            PremiumSubscription.objects.create(
                user=request.user,
                plan=plan,
                transaction=transaction,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=plan.duration_days)
            )
            
            return JsonResponse({'message': 'Payment successful! You are now Premium.'}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f"Error in CashView: {str(e)}")
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
