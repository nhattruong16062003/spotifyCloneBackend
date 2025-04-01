from models.models import Playlist, PlaylistSong, Song
from django.db.models import Max

class PlaylistService:
    @staticmethod
    def add_song_to_playlists(user_id, song_id, playlist_ids):
        """Thêm bài hát vào nhiều playlist của user với thứ tự cao nhất +1"""
        if not playlist_ids:
            return {"error": "Thiếu danh sách playlist_ids"}, 400

        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return {"error": "Bài hát không tồn tại"}, 404

        added_playlists = []
        for playlist_id in playlist_ids:
            try:
                playlist = Playlist.objects.get(id=playlist_id, user_id=user_id)

                # Tìm giá trị order cao nhất trong playlist
                max_order = PlaylistSong.objects.filter(playlist=playlist).aggregate(Max('order'))['order__max']
                new_order = (max_order + 1) if max_order is not None else 1  # Nếu chưa có bài hát thì bắt đầu từ 1

                if not PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                    PlaylistSong.objects.create(playlist=playlist, song=song, order=new_order)
                    added_playlists.append(playlist.name)
            except Playlist.DoesNotExist:
                continue

        if added_playlists:
            return {"message": "Đã thêm bài hát vào các playlist", "playlists": added_playlists}, 201
        return {"message": "Bài hát đã có trong tất cả playlist được chọn"}, 200
    
    @staticmethod
    def create_playlist(user_id, name):
        """Tạo playlist mới cho user"""
        if not name.strip():
            return {"error": "Tên playlist không được để trống"}, 400

        playlist = Playlist.objects.create(name=name, user_id=user_id)

        # Trả về JSON chứa id và name của playlist
        return {"id": playlist.id, "name": playlist.name}, 201
    
    @staticmethod
    def create_album(album_data):
        """Tạo playlist (album) mới cho user"""
        # Lấy dữ liệu từ album_data
        name = album_data.get("name", "").strip()
        description = album_data.get("description", "").strip()
        image_path = album_data.get("image_path")
        user_id = album_data.get("user_id")

        # Kiểm tra tên playlist không được để trống
        if not name:
            return {"error": "Tên playlist không được để trống"}, 400

        try:
            # Tạo playlist mới với dữ liệu từ album_data
            playlist = Playlist.objects.create(
                name=name,
                description=description,
                image_path=image_path,
                user_id=user_id
            )

            # Trả về JSON chứa id và name của playlist cùng mã trạng thái 201
            return {"id": playlist.id, "name": playlist.name}, 201

        except Exception as e:
            # Trả về lỗi nếu có vấn đề khi tạo playlist
            return {"error": f"Failed to create playlist: {str(e)}"}, 500
        

    @staticmethod
    def add_song_to_album(album_id, song_id, user_id):
        try:
            playlist = Playlist.objects.get(id=album_id, user_id=user_id)
            song = Song.objects.get(id=song_id)

            if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                return False

            max_order_result = PlaylistSong.objects.filter(playlist=playlist).aggregate(Max('order'))
            max_order = max_order_result['order__max']
            new_order = (max_order + 1) if max_order is not None else 1

            PlaylistSong.objects.create(
                playlist=playlist,
                song=song,
                order=new_order
            )
            return True

        except Playlist.DoesNotExist:
            return False
        except Song.DoesNotExist:
            return False
        except Exception as e:
            return False
        
    # Trong PlaylistService
    def delete_album(album_id):
        try:
            album = PlaylistSong.objects.get(id=album_id)
            album.delete()
            return True
        except PlaylistSong.DoesNotExist:
            return False
