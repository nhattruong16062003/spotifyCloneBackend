from django.urls import path
from .views.AuthView import AuthView, ActivateAccountView, GoogleLoginView
from .views.HomeView import HomeView
from .views.UserView import UserView
from .views.SongView import SongView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/auth/<str:action>/', AuthView.as_view(), name='auth_action'),
    path('api/auth/activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('api/auth/login/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/user/<int:user_id>/', UserView.as_view(), name='user'),
    path('api/song/', SongView.as_view(), name='add_song'),
    path('api/song/<int:song_id>/', SongView.as_view(), name='update_delete_song'),
]

