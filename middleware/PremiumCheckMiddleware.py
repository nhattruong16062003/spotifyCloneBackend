from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from models.models import PremiumSubscription
from django.utils import timezone

class PremiumCheckMiddleware(MiddlewareMixin):
    # Endpoint CHỈ DÀNH CHO PREMIUM
    PREMIUM_REQUIRED_ENDPOINTS = (
        "/api/premium/update/order-playlist/",
        "/api/premium/update/image/"
    )

    # Endpoint CHỈ DÀNH CHO NON-PREMIUM
    NON_PREMIUM_ONLY_ENDPOINTS = (
        "/api/create-payment/",
        "/api/payment-return/",
        "/api/cash-payment/",
    )

    def process_request(self, request):
        path = request.path

        # Kiểm tra nếu URL nằm trong 2 danh sách cần kiểm soát premium
        if self._is_path_in(path, self.PREMIUM_REQUIRED_ENDPOINTS + self.NON_PREMIUM_ONLY_ENDPOINTS):
            # Nếu chưa đăng nhập → chặn luôn
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # Kiểm tra trạng thái premium của user
            is_premium = self._check_user_premium(request.user)

            # Nếu là endpoint yêu cầu PREMIUM
            if self._is_path_in(path, self.PREMIUM_REQUIRED_ENDPOINTS) and not is_premium:
                return JsonResponse({"error": "Premium membership required"}, status=403)

            # Nếu là endpoint chỉ dành cho NON-PREMIUM
            if self._is_path_in(path, self.NON_PREMIUM_ONLY_ENDPOINTS) and is_premium:
                return JsonResponse({"error": "This action is only for non-premium users"}, status=403)

        # Nếu không thuộc danh sách kiểm soát premium → cho đi tiếp
        return None

    def _is_path_in(self, path, endpoints):
        """Kiểm tra xem path có bắt đầu bằng endpoint nào trong danh sách không."""
        return any(path.startswith(endpoint) for endpoint in endpoints)

    def _check_user_premium(self, user):
        """Kiểm tra user có gói Premium còn hiệu lực hay không."""
        return PremiumSubscription.objects.filter(
            user=user,
            end_date__gt=timezone.now()
        ).exists()
