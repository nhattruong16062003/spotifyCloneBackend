from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from api.serializers.UserSerializer import UserSerializer
from django.utils.crypto import get_random_string
import google.auth.transport.requests
import google.oauth2.id_token
from django.http import HttpResponseRedirect
import requests
from services.AuthService import AuthService
from rest_framework.permissions import AllowAny
from models.role import Role 
from api.helpers.Validate import validate_password,validate_email



User = get_user_model()

class AuthView(APIView):
    # permission_classes = [AllowAny]  # Không yêu cầu xác thực
    def post(self, request, action):
        if action == 'register':
            return self.register(request)
        elif action == 'login':
            return self.login(request)
        elif action == 'refresh':
            return self.refresh_token(request)
        elif action == 'password-reset':
            return self.password_reset(request)
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def register(self, request):
        email = request.data.get('email')
        name = request.data.get('username')
        password = request.data.get('password')
        try:
            role_id = 3
            # Lấy Role với id=3 (nếu tồn tại)
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({
                "error_code": "ROLE_NOT_FOUND", 
                "details": "Role with ID 3 does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)


        # Validate email
        if not validate_email(email):
            return JsonResponse({"error_code": "INVALID_DATA"}, status=400)   

        # Validate password
        if not validate_password(password):
            return JsonResponse({
                "error_code": "INVALID_DATA"
            }, status=400)
            
        if User.objects.filter(email=email).exists():
            return Response({"error_code": "EMAIL_ALREADY_EXISTS"}, status=status.HTTP_400_BAD_REQUEST)
          
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.username = email
            user.name = name
            user.is_active = False
            user.role = role
            user.set_password(password) 
            user.save()
            AuthService.send_activation_email(user, request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error_code": "INVALID_DATA", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        if request.user.is_authenticated:
            return Response({"message": "Already logged in"}, status=status.HTTP_200_OK)
        
        email = request.data.get('email')
        password = request.data.get('password')

        user, error_code = AuthService.authenticate_user(email, password)
        if error_code:
            return Response({"error_code": error_code}, status=status.HTTP_400_BAD_REQUEST)

        # login(request, user)
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role":user.role.id    #nếu muốn trả về tên role:  str(user.role)
        }, status=status.HTTP_200_OK)
        
        
    def refresh_token(self, request):
        refresh_token = request.data.get("refresh")  
        print(f"Before authentication: {refresh_token}")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        tokens, error_code = AuthService.refresh_tokens(refresh_token)
        if error_code:
            return Response({"error_code": error_code}, status=status.HTTP_400_BAD_REQUEST)
        return Response(tokens, status=status.HTTP_200_OK)

    def password_reset(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        success, error = AuthService.reset_password(email)
        if not success:
            if error == "USER_NOT_FOUND":
                return Response({"error_code": "USER_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)

class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Activation link is invalid"}, status=status.HTTP_400_BAD_REQUEST)

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("access_token")
        if not token:
            return Response({"error_code": "ACCESS_TOKEN_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Use Google's token info endpoint to validate the access token and get user info
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"access_token": token},
            )
            if response.status_code != 200:
                return Response({"error_code": "INVALID_GOOGLE_TOKEN"}, status=status.HTTP_400_BAD_REQUEST)

            id_info = response.json()
            email = id_info.get("email")
            google_id = id_info.get("sub") 
            username = id_info.get("name", email) 

            if not email or not google_id:
                return Response({"error_code": "INVALID_GOOGLE_TOKEN"}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra xem email đã được đăng kí trước đó chưa? 
            try:
                user = User.objects.get(email=email)
                # Nếu đã được đăng kí và chưa active
                if not user.is_active:
                    return Response({"error_code": "ACCOUNT_NOT_ACTIVATED"}, status=status.HTTP_400_BAD_REQUEST)

                # Update the google_id if not already set
                if not hasattr(user, 'google_id') or not user.google_id:
                    user.google_id = google_id
                    user.save()

            except User.DoesNotExist:
                # Create a new user if the email does not exist
                user = User.objects.create(
                    username=username,
                    name = username,
                    email=email,
                    google_id=google_id,  # Save the Google ID
                )
                user.is_active = True  # Activate the account by default for social login
                user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role":user.role.id    #nếu muốn trả về tên role:  str(user.role)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Google Login Error: {str(e)}")
            return Response({"error_code": "UNKNOWN_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)