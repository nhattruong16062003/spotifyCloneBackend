from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models.models import Playlist
from django.db import transaction
from services.UploadService import UploadService

class UpdateImagePlaylistView(APIView):
    def patch(self, request):
        """
        Cập nhật ảnh bìa của playlist.
        Payload từ FE (multipart/form-data):
        - data: {"playlistId": 1}
        - files: {"cover": <file ảnh>}
        """
        try:
            # Lấy playlistId từ request.data
            playlist_id = request.data.get("playlistId")
            files = request.FILES

            if not playlist_id:
                return Response(
                    {"error": "playlistId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Kiểm tra playlist có tồn tại không
            try:
                playlist = Playlist.objects.get(id=playlist_id)
            except Playlist.DoesNotExist:
                return Response(
                    {"error": f"Playlist with ID {playlist_id} does not exist"},
                    status=status.HTTP_404_NOT_FOUND
                )

            with transaction.atomic():
                # B1: Upload ảnh bìa nếu có
                image_url = None
                image_name = None
                if "cover" in files:
                    image = files["cover"]
                    image_name = f"images/{image.name}"
                    image_url = UploadService.upload_image_to_s3(image, image_name)

                    # B2: Cập nhật link ảnh mới vào database
                    playlist.image_path = image_url
                    playlist.save()

                else:
                    return Response(
                        {"error": "No cover image provided"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"message": "Playlist image updated successfully", "image_url": image_url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )