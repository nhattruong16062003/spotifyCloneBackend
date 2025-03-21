from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.SongService import SongService
from services.UploadService import UploadService

class SongView(APIView):
    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]
        file_name = f"audio/{file.name}"

        # Gọi service để upload file
        file_url = UploadService.upload_file_to_s3(file, file_name)

        if not file_url:
            return Response({"error": "Failed to upload file"}, status=500)

        # Tạo một bản sao nông của request.data và thêm URL của file
        data = {
            "title": request.data.get("title"),
            "duration": request.data.get("duration"),
            "album": request.data.get("album"),
            "genre": request.data.get("genre"),
            "artist_id": request.data.get("artist_id"), 
            "file_path": file_url
        }

        # Gọi SongService để lưu thông tin bài hát
        song = SongService.add_song(data)
        if not song:
            # Xóa file đã upload nếu lưu vào cơ sở dữ liệu thất bại
            UploadService.delete_file_from_s3(file_name)
            return Response({"error": "Failed to save song"}, status=500)

        return Response({"id": song.id, "title": song.title}, status=status.HTTP_201_CREATED)

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