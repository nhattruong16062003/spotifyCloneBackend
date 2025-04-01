import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from models.models import Playlist, PlaylistSong, Song
from api.serializers.PlaylistSerializer import PlaylistSerializer
from services.PlaylistService import PlaylistService
from django.db.models import Count
from services.UploadService import UploadService
from rest_framework.response import Response
from django.http import JsonResponse

class PlaylistView(APIView):
    def get(self, request, song_id=None):
        user_id = request.user.id  # Lấy user_id

        """API lấy danh sách playlist của user nhưng chưa chứa song_id"""
        if request.path.endswith(f"/api/playlist/user/{song_id}/"):  # Kiểm tra URL
            playlists = Playlist.objects.filter(user_id=user_id).exclude(playlistsong__song_id=song_id)
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
            """API tạo playlist hoặc thêm bài hát vào nhiều playlist"""
            # Kiểm tra người dùng đã login chưa
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)
            data = request.data
            user_id = request.user.id  # Nếu dùng authentication

            if "name" in data:  # Nếu có 'name', thực hiện tạo playlist mới
                user_id = request.user.id  # Nếu dùng authentication

                result, status_code = PlaylistService.create_playlist(user_id, data["name"])
                return Response(result, status=status_code)

            if not request.path.endswith("/api/playlist/add-song/"):
                return Response({"error": "Invalid request path"}, status=status.HTTP_400_BAD_REQUEST)

            # Xử lý thêm bài hát vào playlist (giữ nguyên code cũ)
            song_id = data.get("song_id")
            playlist_ids = data.get("playlists", [])  

            if not song_id or not playlist_ids:
                return Response({"error": "Thiếu song_id hoặc danh sách playlist_ids"}, status=status.HTTP_400_BAD_REQUEST)

            result, status_code = PlaylistService.add_song_to_playlists(user_id, song_id, playlist_ids)
            return Response(result, status=status_code)
      
    
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
                    UploadService.delete_image_from_s3(image_url)  # Sửa đây
                return Response({"error": "Invalid songs data format"}, status=400)

            # Kiểm tra dữ liệu bắt buộc
            if not album_name or not description or not songs:
                if image_url:
                    UploadService.delete_image_from_s3(image_url)  # Sửa đây
                return Response({"error": "Missing required fields: name, description, or songs"}, status=400)

            # B3: Gọi PlaylistService để tạo album và thêm bài hát
            try:
                album_data = {
                    "name": album_name,
                    "description": description,
                    "image_path": image_url,
                    "user_id": user_id,
                }
                album = PlaylistService.create_album(album_data)
                if isinstance(album, tuple):  # Kiểm tra nếu album là tuple
                    album = album[0]  # Lấy phần tử đầu tiên từ tuple (nếu cần)
                if not album:
                    if image_url:
                        UploadService.delete_image_from_s3(image_url)
                    return Response({"error": "Failed to create album"}, status=500)

                # Thêm bài hát vào album
                for song in songs:
                    song_id = song.get("id")
                    if not song_id:
                        PlaylistService.delete_album(album["id"])
                        if image_url:
                            UploadService.delete_image_from_s3(image_url)
                        return Response({"error": "Invalid song data"}, status=400)

                    success = PlaylistService.add_song_to_album(album["id"], song_id, user_id)
                    if not success:
                        PlaylistService.delete_album(album["id"])
                        if image_url:
                            UploadService.delete_image_from_s3(image_url)
                        return Response({"error": f"Failed to add song {song_id} to album"}, status=500)

                return Response({
                    "message": "Album created successfully",
                    "album_id": album["id"]
                }, status=201)

            except Exception as e:
                if image_url:
                    UploadService.delete_image_from_s3(image_url)
                if 'album' in locals() and album:
                    PlaylistService.delete_album(album["id"])
                return Response({"error": f"An error occurred: {str(e)}"}, status=500)

        return Response({"error": "Invalid endpoint"}, status=404)