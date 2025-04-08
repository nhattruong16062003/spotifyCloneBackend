from django.urls import path, include
from .views.AuthView import AuthView, ActivateAccountView, GoogleLoginView
from .views.HomeView import HomeView
from .views.UserView import UserView
from .views.SongView import SongView
from .views.TrendingView import TrendingView
from .views.SongPlayHistoryView import SongPlayHistoryView  
from .views.AccountView import AccountView
from .views.PlaylistView import PlaylistView
from .views.PlanView import PlanDetailView,PlanListView 
from .views.ArtistRegistrationView import ArtistRegistrationView
from .views.ArtistCollabView import FindArtistCollab
from .views.SearchView import SearchView
from .views.PublicProfileView import PublicProfileView

urlpatterns = [
    #PUBLIC
    path('api/', include('payments.urls')),
    path('', HomeView.as_view(), name='home'),
    path('api/auth/<str:action>/', AuthView.as_view(), name='auth_action'),
    path('api/auth/activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('api/auth/login/google/', GoogleLoginView.as_view(), name='google_login'),

    path('api/user/<int:user_id>/', UserView.as_view(), name='user'),
    path('api/song/<int:song_id>/', SongView.as_view(), name='update_delete_song'),

    path('api/trending/songs/', TrendingView.as_view(), name='trending_songs'),
    path('api/trending/playlists/', TrendingView.as_view(), name='trending_playlists'),
    path('api/trending/albums/', TrendingView.as_view(), name='trending_albums'),

    path('api/song/previous/<int:song_id>/', SongView.as_view(), name='previous_song'),
    path('api/song/next/<int:song_id>/', SongView.as_view(), name='next_song'),

    path('api/history/update/', SongPlayHistoryView.as_view(), name='update_play_history'),
    path('api/account/', AccountView.as_view(), name='account'),
    path('api/playlists/songs/<int:playlist_id>/', PlaylistView.as_view(), name='playlist-songs'),

    path('api/playlist/user/<int:song_id>/', PlaylistView.as_view(), name='get_playlists_from_user'),
    path('api/playlist/add-song/', PlaylistView.as_view(), name='add_song_to_playlist'),
    path('api/playlist/create/', PlaylistView.as_view(), name='create_playlist'), 

    path('api/plans/', PlanListView.as_view(), name='plans'), 
    path('api/plans/<int:plan_id>/', PlanDetailView.as_view(), name='plan_detail'),

    path('api/search/', SearchView.as_view(), name='search'),

    #USER
    path('api/public-profile/<int:profile_id>/', AccountView.as_view(), name='public_profile'),
    path('api/public-profile/playlists/<int:profile_id>/', PublicProfileView.as_view(), name='public_playlists'),
    path('api/public-profile/albums/<int:profile_id>/', PublicProfileView.as_view(), name='public_albums'),
    path('api/public-profile/popular-songs/<int:profile_id>/',PublicProfileView.as_view(), name='popular_song'),

    # ARTIST
    path('api/artist/songs/', SongView.as_view(), name='artist_song'),

    path('api/artist/albums/', PlaylistView.as_view(), name='artist_album'),
    path('api/artist/create-album', PlaylistView.as_view(), name='create-album'),

    path('api/artist/song/', SongView.as_view(), name='add_song'), #upload
    path('api/artist/fetch-artist-collab/', FindArtistCollab.as_view(), name='get-artist-collab'), 

    #ADMIN 
    path('api/admin/artist-registration-requests/', ArtistRegistrationView.as_view(), name='artist-registration'),
    path('api/admin/<str:action>/<int:id>/', ArtistRegistrationView.as_view(), name='artist-registration'),
    path('api/admin/accounts/<str:action>/<int:id>/', AccountView.as_view(), name='account'),
    path('api/admin/accounts/',AccountView.as_view(), name='account'),
    
    


]



