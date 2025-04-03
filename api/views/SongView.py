import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.SongService import SongService
from services.UploadService import UploadService
from services.ImageService import ImageService
from services.ArtistCollabService import ArtistCollabService
from django.db import transaction
from models.models import Song, ArtistCollab


class SongView(APIView):
    def post(self, request, *args, **kwargs):
        user_id=request.user.id
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]
        file_name = f"audio/{file.name}"

        # Gọi service để upload file
        file_url = UploadService.upload_mp3_to_s3(file, file_name)
        if not file_url:
            return Response({"error": "Failed to upload file"}, status=500)

        # Upload image nếu có
        image_url = None
        if "image" in request.FILES:
            image = request.FILES["image"]
            image_name = f"images/{image.name}"
            image_url = UploadService.upload_image_to_s3(image, image_name)
            if not image_url:
                return Response({"error": "Failed to upload image"}, status=500)
            
        # Tạo một bản sao nông của request.data và thêm URL của file và image
        data = {
            "title": request.data.get("title"),
            "duration": request.data.get("duration"),
            "description": request.data.get("description"),
            "genre": request.data.get("genre"),
            "user_id": user_id, 
            "mp3_path": file_url,
            "image_path": image_url
        }

        try:
            with transaction.atomic():  # Bọc trong transaction
                # Gọi SongService để lưu thông tin bài hát
                song = SongService.add_song(data)
                if not song:
                    raise Exception("Failed to save song")

                # Lấy dữ liệu từ request
                artist_collab_json = request.data.get("artist_collab")
                if not artist_collab_json:
                    raise Exception("Missing artist_collab data")

                # Parse chuỗi JSON thành danh sách Python
                try:
                    artist_ids = json.loads(artist_collab_json)
                except json.JSONDecodeError:
                    raise Exception("Invalid artist_collab JSON format")

                # Chỉ gọi service nếu artist_ids không rỗng
                if artist_ids:  # Kiểm tra danh sách có giá trị
                    result = ArtistCollabService.create_artist_collabs(song.id, artist_ids)
                    if not result:  # Giả sử result trả về False hoặc None khi thất bại
                        raise Exception("Failed to create artist collaborations")

                # Nếu mọi thứ thành công, trả về response
                return Response({"id": song.id, "title": song.title}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Nếu có lỗi, transaction sẽ rollback, xóa file đã upload trên S3
            if image_url:
                UploadService.delete_image_from_s3(image_url)
            if file_url:
                UploadService.delete_file_from_s3(file_url)
            return Response({"error": str(e)}, status=500)

    def get(self, request, song_id=None, *args, **kwargs):
        path = request.path  # Lấy đường dẫn URL
        user_id=request.user.id

        if 'api/song/previous/' in path:  # Nếu URL có chứa "previous", lấy bài hát trước đó
            song = SongService.get_previous_song(song_id, user_id)
            if not song:
                return Response({"error": "No previous song found"}, status=status.HTTP_404_NOT_FOUND)

        elif 'api/song/next/' in path:  # Nếu URL có chứa "next", lấy bài hát sau đó
            song = SongService.get_next_song(song_id)
            if not song:
                return Response({"error": "No next song found"}, status=status.HTTP_404_NOT_FOUND)

        elif 'api/song/' in path:  # Nếu URL có chứa "song", lấy thông tin bài hát theo ID
            song = SongService.get_song(song_id)
            if not song:
                return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
        elif 'api/artist/songs/' in path:  # Nếu URL có chứa "artist/songs"
            songs = SongService.get_songs_by_artist(user_id)
            return Response(songs, status=status.HTTP_200_OK)
            
        else:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        image_info = None
        if song.image_path:
            image_info = ImageService.get_image_info(song.image_path)

        song = Song.objects.get(id=song_id)
        # Lấy danh sách các nghệ sĩ hợp tác
        collab_artists = ArtistCollab.objects.filter(song=song).select_related('user')
        collab_artist_names = [collab.user.name for collab in collab_artists if collab.user.name]

        return Response({
            "id": song.id,
            "title": song.title,
            "artist": song.user.name,
            "collab_artists": collab_artist_names,  # Danh sách nghệ sĩ hợp tác
            "description": song.description,
            "genre": song.genre,
            "duration": song.duration,
            "mp3_path": song.mp3_path,
            "image_path": song.image_path,
            "image_info": image_info
        }, status=status.HTTP_200_OK)    

    def put(self, request, song_id, *args, **kwargs):
        data = request.data
        song = SongService.update_song(song_id, data)
        if song:
            return Response({"id": song.id, "title": song.title}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, song_id, *args, **kwargs):
        success = SongService.delete_song(song_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)