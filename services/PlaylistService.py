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
                    print(f"Đã thêm {song.title} vào playlist {playlist.name} với order {new_order}")
                    added_playlists.append(playlist.name)
                else:
                    print(f"Bài hát {song.title} đã có trong playlist {playlist.name}")
            except Playlist.DoesNotExist:
                print(f"Playlist ID {playlist_id} không tồn tại hoặc không thuộc user {user_id}")
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
