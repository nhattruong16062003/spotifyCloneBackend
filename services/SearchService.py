from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from models.models import User, Song, Playlist

class SearchService:

    @staticmethod
    def search_users(keyword, limit, offset):
        """Tìm kiếm users theo keyword (role_id=3) với phân trang"""
         # Chuyển đổi limit và offset thành số nguyên
        limit = int(limit)
        offset = int(offset) * limit

        # Truy vấn và lọc user (vai trò user thường, role_id=3)
        users = User.objects.filter(
            name__icontains=keyword,
            role_id=3,
            is_active=True,
            is_ban=False
        ).distinct()

        # Tính toán phân trang
        paginated_results = users[offset:offset+limit]

        return paginated_results
    
    @staticmethod
    def search_artists(keyword, limit, offset):
        """
        Tìm kiếm artists theo keyword (role_id=2) với thứ tự ưu tiên:
        1. Tên artist
        2. Tên bài hát của artist (nghệ sĩ chính và collab)
        3. Tên playlist của artist
        Args:
            keyword (str): Từ khóa tìm kiếm
            limit (int): Số lượng kết quả tối đa trên mỗi trang
            offset (int): Vị trí bắt đầu (dùng cho phân trang)
        """
        # Chuyển đổi limit và offset thành số nguyên
        limit = int(limit)
        offset = int(offset) * limit

        # 1. Tìm artist theo tên
        artists_by_name = User.objects.filter(
            Q(name__icontains=keyword) &
            Q(role_id=2) &
            Q(is_active=True) &
            Q(is_ban=False)
        ).distinct()

        # 2.1 Nghệ sĩ chính (user trực tiếp của Song)
        artists_by_song_main = User.objects.filter(
            Q(song__title__icontains=keyword) &
            Q(role_id=2) &
            Q(is_active=True) &
            Q(is_ban=False)
        ).distinct()

        # 2.2 Nghệ sĩ collab (qua bảng ArtistCollab)
        artists_by_song_collab = User.objects.filter(
            Q(artistcollab__song__title__icontains=keyword) &
            Q(role_id=2) &
            Q(is_active=True) &
            Q(is_ban=False)
        ).distinct()

        # 3. Tìm artist theo tên playlist
        artists_by_playlist = User.objects.filter(
            Q(playlist__name__icontains=keyword) &
            Q(role_id=2) &
            Q(is_active=True) &
            Q(is_ban=False)
        ).distinct()

        # Kết hợp các kết quả theo thứ tự ưu tiên
        all_artists = list(dict.fromkeys(
            list(artists_by_name) +
            list(artists_by_song_main) +
            list(artists_by_song_collab) +
            list(artists_by_playlist)
        ))

        # Tính toán phân trang
        paginated_results = all_artists[offset:offset+limit]

        return paginated_results

    @staticmethod
    def search_songs(keyword, limit, offset):
        """
        Tìm kiếm songs theo keyword với thứ tự ưu tiên:
        1. Trùng tên bài hát
        2. Trùng tên ca sĩ chính
        3. Trùng tên ca sĩ collab
        4. Trùng tên playlist do artist (role_id=2) tạo
        """
        # Chuyển đổi limit và offset thành số nguyên
        limit = int(limit)
        offset = int(offset) * limit

        # 1. Tìm bài hát theo tên bài hát
        songs_by_title = Song.objects.filter(
            Q(title__icontains=keyword)
        ).distinct()

        # 2. Tìm bài hát theo tên ca sĩ chính
        songs_by_main_artist = Song.objects.filter(
            Q(user__name__icontains=keyword) &
            Q(user__role_id=2) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # 3. Tìm bài hát theo tên ca sĩ collab
        songs_by_collab_artist = Song.objects.filter(
            Q(artistcollab__user__name__icontains=keyword) &
            Q(artistcollab__user__role_id=2) &
            Q(artistcollab__user__is_active=True) &
            Q(artistcollab__user__is_ban=False)
        ).distinct()

        # 4. Tìm bài hát trong playlist do artist (role_id=2) tạo
        songs_by_playlist = Song.objects.filter(
            Q(playlistsong__playlist__name__icontains=keyword) &
            Q(playlistsong__playlist__user__role_id=2) &
            Q(playlistsong__playlist__user__is_active=True) &
            Q(playlistsong__playlist__user__is_ban=False)
        ).distinct()

        # Kết hợp các kết quả theo thứ tự ưu tiên
        all_songs = list(dict.fromkeys(
            list(songs_by_title) +
            list(songs_by_main_artist) +
            list(songs_by_collab_artist) +
            list(songs_by_playlist)
        ))

         # Tính toán phân trang
        paginated_results = all_songs[offset:offset+limit]

        return paginated_results

    @staticmethod
    def search_playlists(keyword, limit, offset):
        """
        Tìm kiếm playlists theo keyword với thứ tự ưu tiên:
        1. Tên playlist
        2. Tên bài hát có trong playlist
        3. Tên ca sĩ có bài hát trong playlist (chỉ lấy user có role_id=3)
        """

        # Chuyển đổi limit và offset thành số nguyên
        limit = int(limit)
        offset = int(offset) * limit

        # 1. Tìm playlist theo tên
        playlists_by_name = Playlist.objects.filter(
            Q(name__icontains=keyword) &
            Q(user__role_id=3) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # 2. Tìm playlist theo tên bài hát trong playlist
        playlists_by_song = Playlist.objects.filter(
            Q(playlistsong__song__title__icontains=keyword) &
            Q(user__role_id=3) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # 3. Tìm playlist theo tên ca sĩ có bài hát trong playlist
        playlists_by_artist = Playlist.objects.filter(
            Q(playlistsong__song__user__name__icontains=keyword) &
            Q(user__role_id=3) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # Kết hợp các kết quả theo thứ tự ưu tiên
        all_playlists = list(dict.fromkeys(
            list(playlists_by_name) +
            list(playlists_by_song) +
            list(playlists_by_artist)
        ))

        # Tính toán phân trang
        paginated_results = all_playlists[offset:offset+limit]

        return paginated_results
        
    @staticmethod
    def search_albums(keyword, limit, offset):
        """
        Tìm kiếm albums theo keyword (albums là playlists của user với role_id=2) với thứ tự ưu tiên:
        1. Tên album (playlist)
        2. Tên bài hát có trong playlist
        3. Tên ca sĩ có bài hát trong playlist
        Nếu không tìm thấy, trả về một album ngẫu nhiên của user có role_id=2
        """

        # Chuyển đổi limit và offset thành số nguyên
        limit = int(limit)
        offset = int(offset) * limit

        # 1. Tìm album theo tên
        albums_by_name = Playlist.objects.filter(
            Q(name__icontains=keyword) &
            Q(user__role_id=2) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # 2. Tìm album theo tên bài hát trong playlist
        albums_by_song = Playlist.objects.filter(
            Q(playlistsong__song__title__icontains=keyword) &
            Q(user__role_id=2) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # 3. Tìm album theo tên ca sĩ có bài hát trong playlist
        albums_by_artist = Playlist.objects.filter(
            Q(playlistsong__song__user__name__icontains=keyword) &
            Q(user__role_id=2) &
            Q(user__is_active=True) &
            Q(user__is_ban=False)
        ).distinct()

        # Kết hợp các kết quả theo thứ tự ưu tiên
        all_albums = list(dict.fromkeys(
            list(albums_by_name) +
            list(albums_by_song) +
            list(albums_by_artist)
        ))

        
        # Tính toán phân trang
        paginated_results = all_albums[offset:offset+limit]

        return paginated_results

    @staticmethod
    def search(data_type, keyword, limit, offset):
        """Tìm kiếm dữ liệu dựa trên data_type và keyword"""
        if data_type == "users":
            return SearchService.search_users(keyword, limit, offset)
        elif data_type == "artists":
            return SearchService.search_artists(keyword, limit, offset)
        elif data_type == "songs":
            return SearchService.search_songs(keyword, limit, offset)
        elif data_type == "playlists":
            return SearchService.search_playlists(keyword, limit, offset)
        elif data_type == "albums":
            return SearchService.search_albums(keyword, limit, offset)
        else:
            return None