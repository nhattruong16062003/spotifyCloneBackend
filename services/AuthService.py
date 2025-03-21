from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.urls import reverse
from django.utils.crypto import get_random_string

User = get_user_model()

class AuthService:
    @staticmethod
    def send_activation_email(user, request):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = f"{request.scheme}://{request.get_host()}{activation_link}"
        subject = 'Activate your account'
        message = f'Hi {user.username}, please click the link to activate your account: {activation_url}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)

    @staticmethod
    def authenticate_user(email, password):
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return None, "ACCOUNT_NOT_ACTIVATED"
        except User.DoesNotExist:
            return None, "INVALID_CREDENTIALS"

        user = authenticate(username=email, password=password)
        if user is None:
            return None, "INVALID_CREDENTIALS"
        return user, None

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    # @staticmethod
    # def refresh_tokens(refresh_token):
    #     try:
    #         token = RefreshToken(refresh_token)
    #         print(f"Before authentication: {token.user}") 
    #         access_token = str(token.access_token)
    #         new_refresh_token = str(RefreshToken.for_user(token.user))
    #         print(f"Before authentication: {access_token}")  # Có thể là AnonymousUser
    #         return {"access": access_token, "refresh": new_refresh_token}, None
    #     except TokenError:
    #         return None, "INVALID_REFRESH_TOKEN"
    @staticmethod
    def refresh_tokens(refresh_token):
        try:
            # Giải mã refresh token
            token = RefreshToken(refresh_token)

            # Lấy user_id từ token
            user_id = token.get("user_id")
            if not user_id:
                return None, "INVALID_REFRESH_TOKEN"

            # Lấy user từ database
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None, "USER_NOT_FOUND"

            print(f"Before authentication: {user}") 
            # Tạo access token mới
            access_token = str(token.access_token)

            # Tạo refresh token mới
            new_refresh_token = str(RefreshToken.for_user(user))

            return {"access": access_token, "refresh": new_refresh_token}, None
        except TokenError:
            return None, "INVALID_REFRESH_TOKEN"

    @staticmethod
    def reset_password(email):
        try:
            user = User.objects.get(email=email)
            new_password = get_random_string(length=8)
            user.set_password(new_password)
            user.save()
            send_mail(
                'Password Reset',
                f'Your new password is: {new_password}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return True, None
        except User.DoesNotExist:
            return False, "USER_NOT_FOUND"
        except Exception as e:
            return False, str(e)