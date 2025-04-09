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
from models.user import User
from models.artist_registration import ArtistRegistration
from services.UploadService import UploadService
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from services.EmailService import send_custom_email

User = get_user_model()

class AuthService:
    # @staticmethod
    # def send_activation_email(user, request):
    #     token = default_token_generator.make_token(user)
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
    #     # activation_url = f"{request.scheme}://{request.get_host()}{activation_link}"
    #     activation_url = f"http://localhost:3000/activate/{uid}/{token}"
    #     subject = 'Activate your account'
    #     message = f'Hi {user.username}, please click the link to activate your account: {activation_url}'
    #     email_from = settings.EMAIL_HOST_USER
    #     recipient_list = [user.email]
    #     send_mail(subject, message, email_from, recipient_list)

    @staticmethod
    def send_activation_email(user, request):
        # Tạo token và UID cho link kích hoạt
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = f"http://localhost:3000/activate/{uid}/{token}"  # URL frontend

        # Gửi email bằng send_custom_email từ EmailService
        send_custom_email(
            subject="Kích hoạt tài khoản của bạn",
            username=user.username,
            message="Vui lòng nhấn vào liên kết bên dưới để kích hoạt tài khoản của bạn.",
            link=activation_url,
            recipient_email=user.email
        )

    @staticmethod
    def authenticate_user(email, password):
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return None, "ACCOUNT_NOT_ACTIVATED"
            elif user.is_ban: 
                return None, "ACCOUNT_WAS_BAN"
        except User.DoesNotExist:
            return None, "INVALID_CREDENTIALS"

        user = authenticate(username=email, password=password)
        if user is None:
            return None, "INVALID_CREDENTIALS"
        return user, None


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
            # Tạo cặp token mới hoàn toàn
            new_refresh = RefreshToken.for_user(user)
            access_token = str(new_refresh.access_token)  # Access token mới
            new_refresh_token = str(new_refresh)          # Refresh token mới

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





    @staticmethod
    def register_artist(data, files):
        """
        Xử lý đăng ký nghệ sĩ, bao gồm việc upload ảnh và kiểm tra thông tin đầu vào.
        """
        artist_name = data.get("artistName")
        phone = data.get("phone")
        email = data.get("email")
        bio = data.get("bio")
        social_link = data.get("socialLink")

        # Trích xuất files ảnh
        proof_images = files.getlist("proofImages")
        artist_images = files.getlist("artistImages")

        # Validate dữ liệu đầu vào
        if not all([artist_name, phone, email]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Kiểm tra email và phone đã tồn tại
        if User.objects.filter(email=email).exists():
            return Response(
                {"error_code": "EMAIL_ALREADY_REGISTERED"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if ArtistRegistration.objects.filter(email=email).exists():
            return Response(
                {"error_code": "EMAIL_ALREADY_REGISTERED"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if ArtistRegistration.objects.filter(phone_number=phone).exists():
            return Response(
                {"error_code": "PHONE_ALREADY_REGISTERED"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Bắt đầu transaction để bảo toàn dữ liệu
        with transaction.atomic():
            uploaded_proof_images = []
            uploaded_artist_images = []

            try:
                # Upload proof images
                for file in proof_images:
                    uploaded_url = UploadService.upload_image_to_s3(file, file.name)
                    uploaded_proof_images.append(uploaded_url)

                # Upload artist images
                for file in artist_images:
                    uploaded_url = UploadService.upload_image_to_s3(file, file.name)
                    uploaded_artist_images.append(uploaded_url)

                # Tạo ArtistRegistrationRequest
                artist_request = ArtistRegistration.objects.create(
                    artist_name=artist_name,
                    phone_number=phone,
                    email=email,
                    bio=bio,
                    social_links=social_link,
                    identity_proof=",".join(uploaded_proof_images) if uploaded_proof_images else "",
                    artist_image=",".join(uploaded_artist_images) if uploaded_artist_images else ""
                )

                return Response(
                    {"message": "Artist registration request successfully created"},
                    status=status.HTTP_201_CREATED
                )

            except Exception as upload_error:
                # Cleanup: Xóa các ảnh đã upload nếu có lỗi
                for url in uploaded_proof_images + uploaded_artist_images:
                    image_name = url.split("/")[-1]
                    UploadService.delete_image_from_s3(image_name)
                # Rollback toàn bộ giao dịch nếu xảy ra lỗi
                raise Exception(f"Image upload failed: {str(upload_error)}")
        