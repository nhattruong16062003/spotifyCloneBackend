from django.urls import path
from .views.AuthView import AuthView, ActivateAccountView, GoogleLoginView
from .views.HomeView import HomeView
from .views.UserView import UserView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/auth/<str:action>/', AuthView.as_view(), name='auth_action'),
    path('api/auth/activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('api/auth/login/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/user/<int:user_id>/', UserView.as_view(), name='user'),
    ]

