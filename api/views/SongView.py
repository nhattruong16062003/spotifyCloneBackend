from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.SongService import SongService
from services.UploadService import UploadService
from services.ImageService import ImageService

class SongView(APIView):
    def post(self, request, *args, **kwargs):
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
            "user_id": request.data.get("user_id"), 
            "mp3_path": file_url,
            "image_path": image_url
        }

        # Gọi SongService để lưu thông tin bài hát
        song = SongService.add_song(data)
        if not song:
            # Xóa file đã upload nếu lưu vào cơ sở dữ liệu thất bại
            UploadService.delete_file_from_s3(file_name)
            if image_url:
                UploadService.delete_file_from_s3(image_name)
            return Response({"error": "Failed to save song"}, status=500)

        return Response({"id": song.id, "title": song.title}, status=status.HTTP_201_CREATED)

    # def get(self, request, song_id, *args, **kwargs):
    #     song = SongService.get_song(song_id)
    #     if not song:
    #         return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)

    #     image_info = None
    #     if song.image_path:
    #         image_info = ImageService.get_image_info(song.image_path)

    #     return Response({
    #         "id": song.id,
    #         "title": song.title,
    #         "artist": song.user.username,
    #         "album": song.album,
    #         "genre": song.genre,
    #         "duration": song.duration,
    #         "mp3_path": song.mp3_path,
    #         "image_path": song.image_path,
    #         "image_info": image_info
    #     }, status=status.HTTP_200_OK)
    def get(self, request, song_id=None, user_id=None, *args, **kwargs):
        path = request.path  # Lấy đường dẫn URL

        if 'previous' in path:  # Nếu URL có chứa "previous", lấy bài hát trước đó
            song = SongService.get_previous_song(song_id, user_id)
            if not song:
                return Response({"error": "No previous song found"}, status=status.HTTP_404_NOT_FOUND)

        elif 'next' in path:  # Nếu URL có chứa "next", lấy bài hát sau đó
            song = SongService.get_next_song(song_id, user_id)
            if not song:
                return Response({"error": "No next song found"}, status=status.HTTP_404_NOT_FOUND)

        elif 'song' in path:  # Nếu URL có chứa "song", lấy thông tin bài hát theo ID
            song = SongService.get_song(song_id)
            if not song:
                return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        image_info = None
        if song.image_path:
            image_info = ImageService.get_image_info(song.image_path)

        return Response({
            "id": song.id,
            "title": song.title,
            "artist": song.user.username,
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