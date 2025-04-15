import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models.models import Song, Playlist, PlaylistSong,User
from api.serializers.PlaylistSerializer import PlaylistSerializer
from api.serializers.SongSerializer import SongSerializer  # Import SongSerializer
from services.PlaylistService import PlaylistService
from django.db.models import Count
from services.UploadService import UploadService
from rest_framework.response import Response
from django.http import JsonResponse
from django.db import transaction

class PlaylistView(APIView):
    def get(self, request, song_id=None, playlist_id=None):
        user_id = request.user.id  # Lấy user_id
        """API lấy danh sách playlist của user nhưng chưa chứa song_id"""
        if request.path.startswith(f"/api/playlist/user/"):  # Kiểm tra URL
            playlists = Playlist.objects.filter(user_id = user_id)
            if song_id is not None:
                playlists = playlists.exclude(playlistsong__song_id=song_id)
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.path.endswith(f"/api/playlists/songs/{playlist_id}/"):
            try:
                # Lấy playlist theo ID
                playlist = Playlist.objects.get(id=playlist_id)

                isOwner = False

                if request.user.is_authenticated:
                    active_premium = request.user.get_active_premium()
                    is_premium = bool(active_premium)
                    user_role=request.user.role_id
                    if user_role == 3 and playlist.user_id == user_id and is_premium:
                        isOwner = True
                
                # Serialize thông tin playlist
                playlist_serializer = PlaylistSerializer(playlist)
                
                # Lấy danh sách bài hát từ bảng PlaylistSong dựa vào playlist_id
                playlist_songs = PlaylistSong.objects.filter(playlist_id=playlist_id).select_related('song')
                
                # Serialize dữ liệu bài hát và thêm trường order
                songs_data = []
                for ps in playlist_songs:
                    song_data = SongSerializer(ps.song).data  # Serialize bài hát
                    song_data['order'] = ps.order  # Thêm trường order từ PlaylistSong
                    songs_data.append(song_data)
                
                # Trả về cả thông tin playlist và danh sách bài hát
                return Response({
                    "playlist": playlist_serializer.data,
                    "songs": songs_data,
                    "isOwner": isOwner
                }, status=status.HTTP_200_OK)
            except Playlist.DoesNotExist:
                return Response({"error": "Playlist not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
         # Kiểm tra đường dẫn api/artist/albums/
        if request.path.endswith("/api/artist/albums/"):            
            # Lọc playlist theo user_id và lấy các trường cần thiết
            playlists = Playlist.objects.filter(user_id=user_id) \
                .annotate(song_count=Count('playlistsong'))  # Thêm số lượng bài hát vào mỗi playlist

            # Lấy danh sách các playlist và số lượng bài hát
            playlist_data = playlists.values('image_path', 'created_at', 'name', 'song_count')

            return Response(list(playlist_data), status=status.HTTP_200_OK)
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.path.endswith("api/playlist/create/"):            
            """API tạo playlist"""
            # Kiểm tra người dùng đã login chưa
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)
            data = request.data
            user_id = request.user.id  # Nếu dùng authentication

            if "name" in data:  # Nếu có 'name', thực hiện tạo playlist mới
                user_id = request.user.id  # Nếu dùng authentication

                result, status_code = PlaylistService.create_playlist(user_id, data["name"])
                return Response(result, status=status_code)
            
            return Response({"error": "Invalid request path"}, status=status.HTTP_400_BAD_REQUEST)


        if request.path.endswith("/api/playlist/add-song/"):
            # Kiểm tra người dùng đã login chưa
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)
            data = request.data
            user_id = request.user.id  # Nếu dùng authentication
            # Xử lý thêm bài hát vào playlist

            song_id = data.get("song_id")
            playlist_ids = data.get("playlists", [])  

            if not song_id or not playlist_ids:
                return Response({"error": "Thiếu song_id hoặc danh sách playlist_ids"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                with transaction.atomic():  # Bọc trong transaction
                    result, status_code = PlaylistService.add_song_to_playlists(user_id, song_id, playlist_ids)
                    if status_code >= 400:  # Nếu service trả về lỗi
                        raise Exception(result.get("error", "Failed to add song to playlists"))
                    return Response(result, status=status_code)
            except Exception as e:
                # Nếu có lỗi, transaction sẽ tự động rollback
                return Response({"error": str(e)}, status=500)
    
        if request.path.endswith("api/artist/create-album"):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            data = request.POST
            files = request.FILES
            user_id = request.user.id

            # B1: Upload ảnh bìa nếu có
            image_url = None
            image_name = None
            if "cover" in files:
                image = files["cover"]
                image_name = f"images/{image.name}"
                image_url = UploadService.upload_image_to_s3(image, image_name)
                if not image_url:
                    return Response({"error": "Failed to upload image"}, status=500)

            # B2: Chuẩn bị dữ liệu để tạo album
            album_name = data.get("name", "").strip()
            description = data.get("description", "").strip()
            songs_json = data.get("songs", "[]")
            
            try:
                songs = json.loads(songs_json)
            except json.JSONDecodeError:
                if image_url:
                    UploadService.delete_image_from_s3(image_url)
                return Response({"error": "Invalid songs data format"}, status=400)

            # Kiểm tra dữ liệu bắt buộc
            if not album_name or not description or not songs:
                if image_url:
                    UploadService.delete_image_from_s3(image_url)
                return Response({"error": "Missing required fields: name, description, or songs"}, status=400)

            # B3: Bao bọc các thao tác DB trong transaction
            try:
                with transaction.atomic():  # Bắt đầu transaction
                    # Tạo album
                    album_data = {
                        "name": album_name,
                        "description": description,
                        "image_path": image_url,
                        "user_id": user_id,
                    }
                    album = PlaylistService.create_album(album_data)
                    if isinstance(album, tuple):  # Kiểm tra nếu album là tuple
                        album = album[0]
                    if not album:
                        raise Exception("Failed to create album")

                    # Thêm bài hát vào album
                    for song in songs:
                        song_id = song.get("id")
                        if not song_id:
                            raise Exception("Invalid song data")
                        success = PlaylistService.add_song_to_album(album["id"], song_id, user_id)
                        if not success:
                            raise Exception(f"Failed to add song {song_id} to album")

                    # Nếu mọi thứ thành công, transaction sẽ tự động commit
                    return Response({
                        "message": "Album created successfully",
                        "album_id": album["id"]
                    }, status=201)
 
            except Exception as e:
                # Nếu có lỗi, transaction sẽ rollback tự động
                if image_url:
                    UploadService.delete_image_from_s3(image_url)
                return Response({"error": f"An error occurred: {str(e)}"}, status=500)

        return Response({"error": "Invalid endpoint"}, status=404)


    def get_albums_by_id(self, request):
        """
        API lấy danh sách album của user
        """
        user_id = request.user.id