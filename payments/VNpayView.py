import logging
import json
import hashlib
import hmac
import urllib.parse
import time
import uuid
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .payments_config import VNPAY_TMN_CODE, VNPAY_HASH_SECRET, VNPAY_URL, VNPAY_RETURN_URL
from .models import Transaction 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from models.premium_plan import PremiumPlan
from models.premium_subscription import PremiumSubscription
logger = logging.getLogger(__name__)  # Khai báo logger

class VNpayView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            # Kiểm tra người dùng đã đăng nhập chưa
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)
            
            user_id = request.user.id

            # Kiểm tra user có đang sử dụng gói Premium không
            existing_subscription = PremiumSubscription.objects.filter(
                user_id=user_id,
                end_date__gte=timezone.now()  # Gói Premium còn hạn
            ).exists()

            if existing_subscription:
                return JsonResponse({'error': 'User already has an active premium subscription'}, status=401)


            # Nhận dữ liệu từ request
            data = json.loads(request.body)
            plan_id = data.get('plan_id')

            # Kiểm tra nếu không có plan_id
            if not plan_id:
                return JsonResponse({'error': 'plan_id is required'}, status=400)
            
            # Lấy thông tin gói từ database
            try:
                plan = PremiumPlan.objects.get(id=plan_id)
                amount = int(plan.price)  # Đảm bảo amount là số nguyên
            except PremiumPlan.DoesNotExist:
                return JsonResponse({'error': 'Plan not found'}, status=404)
            
            # Tạo mã giao dịch duy nhất
            txn_ref = str(uuid.uuid4())

            # Lưu giao dịch vào database
            payment = Transaction.objects.create(
                user=request.user,
                txn_ref=txn_ref,
                amount=amount,
                payment_method="vnpay",
                order_info=f"Thanh toán gói {plan.name}",
                status='pending'
            )

            # Tạo các tham số cần thiết cho VNPay
            vnp_params = {
                'vnp_Version': '2.1.0',
                'vnp_Command': 'pay',
                'vnp_Amount': amount * 100,  # VNPay yêu cầu nhân 100
                'vnp_CurrCode': 'VND',
                'vnp_TxnRef': txn_ref,
                'vnp_OrderInfo': f"Thanh toán gói {plan.name}",
                'vnp_OrderType': '250000',
                'vnp_Locale': 'vn',
                'vnp_ReturnUrl': VNPAY_RETURN_URL,
                'vnp_IpAddr': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'vnp_CreateDate': time.strftime('%Y%m%d%H%M%S'),
                'vnp_TmnCode': VNPAY_TMN_CODE,
            }

          # Sắp xếp và mã hóa các tham số
            sorted_params = sorted(vnp_params.items())
            query_string = urllib.parse.urlencode(sorted_params)
            sign_data = query_string.encode('utf-8')
            vnp_hash_secret = VNPAY_HASH_SECRET.encode('utf-8')
            signature = hmac.new(vnp_hash_secret, sign_data, hashlib.sha512).hexdigest()
            vnp_params['vnp_SecureHash'] = signature

            # Tạo URL thanh toán
            payment_url = f"{VNPAY_URL}?{urllib.parse.urlencode(vnp_params)}"

            return JsonResponse({'paymentUrl': payment_url})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f"Error in create_payment: {str(e)}")  # Ghi log lỗi
            return JsonResponse({'error': f'Internal Server Error: {str(e)}'}, status=500)

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        try:
            # Lấy dữ liệu từ VNPay
            vnp_params = request.GET.dict()
            logger.debug(f"Received VNPay parameters: {vnp_params}")

            # Kiểm tra chữ ký (checksum)
            vnp_secure_hash = vnp_params.pop('vnp_SecureHash', None)
            sorted_params = sorted(vnp_params.items())
            query_string = urllib.parse.urlencode(sorted_params)
            sign_data = query_string.encode('utf-8')
            vnp_hash_secret = VNPAY_HASH_SECRET.encode('utf-8')
            calculated_hash = hmac.new(vnp_hash_secret, sign_data, hashlib.sha512).hexdigest()

            if vnp_secure_hash != calculated_hash:
                return Response({"message": "Dữ liệu không hợp lệ!"}, status=400)

            txn_ref = vnp_params.get('vnp_TxnRef')
            response_code = vnp_params.get('vnp_ResponseCode')

            try:
                # Tìm giao dịch
                payment = Transaction.objects.get(txn_ref=txn_ref)

                # Kiểm tra xem PremiumSubscription đã tồn tại chưa
                subscription_exists = PremiumSubscription.objects.filter(
                    user=payment.user,
                    transaction_id=payment.id
                ).exists()

                if subscription_exists:
                    logger.info(f"Giao dịch {txn_ref} đã được xử lý trước đó cho user {payment.user.email}")
                    return Response({
                        "message": "Thanh toán đã được xử lý trước đó! Bạn đã là Premium."
                    }, status=200)

                # Cập nhật trạng thái giao dịch nếu chưa cập nhật
                if payment.status != 'success' and response_code == '00':
                    payment.response_code = response_code
                    payment.status = 'success'
                    payment.save()
                elif payment.status == 'success' and response_code != '00':
                    logger.warning(f"Giao dịch {txn_ref} đã được đánh dấu success nhưng VNPay trả về {response_code}")
                elif payment.status == 'failed':
                    return Response({
                        "message": "Giao dịch này đã thất bại trước đó!"
                    }, status=400)

                # Chỉ xử lý nếu response_code là '00' (thành công)
                if response_code == '00':
                    # Lấy user và plan từ giao dịch
                    user = payment.user
                    plan = PremiumPlan.objects.get(price=payment.amount)

                    # Tạo bản ghi PremiumSubscription nếu chưa tồn tại
                    if not subscription_exists:
                        subscription = PremiumSubscription.objects.create(
                            user=user,
                            plan=plan,
                            transaction_id=payment.id,  
                            start_date=timezone.now(),
                            end_date=timezone.now() + timedelta(days=plan.duration_days)
                        )
                        logger.info(f"Tạo gói Premium thành công cho {user.email} | Gói: {plan.name}")

                    return Response({
                        "message": "Thanh toán thành công! Bạn đã được nâng cấp lên Premium."
                    }, status=200)
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({
                        "message": "Thanh toán thất bại! Vui lòng thử lại sau."
                    }, status=400)

            except Transaction.DoesNotExist:
                return Response({"message": "Không tìm thấy giao dịch!"}, status=404)
            except PremiumPlan.DoesNotExist:
                return Response({"message": "Không tìm thấy gói premium!"}, status=404)

        except Exception as e:
            logger.error(f"Lỗi xử lý yêu cầu VNPay: {str(e)}")
            return Response({"message": "Yêu cầu không hợp lệ!"}, status=400)