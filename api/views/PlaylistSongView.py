from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models.models import PlaylistSong
from django.db import transaction

class PlaylistSongView(APIView):
    def patch(self, request):
        """
        Cập nhật lại thứ tự bài hát trong playlist (theo danh sách từ FE)
        Payload FE gửi lên dạng:
        {
            "playlistId": 1,
            "listSong": [5, 2, 8]  # Danh sách các id bài hát
        }
        """
        try:
            playlist_id = request.data.get("playlistId")
            list_song = request.data.get("listSong")

            if not playlist_id or not isinstance(list_song, list):
                return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for index, song_id in enumerate(list_song):
                    if not isinstance(song_id, int):
                        return Response(
                            {"error": f"ID bài hát {song_id} không hợp lệ"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Cập nhật thứ tự cho mỗi bài hát
                    updated = PlaylistSong.objects.filter(
                        playlist_id=playlist_id,
                        song_id=song_id
                    ).update(order=index)

                    if updated == 0:
                        return Response(
                            {"error": f"Bài hát với ID {song_id} không tồn tại trong playlist {playlist_id}"},
                            status=status.HTTP_404_NOT_FOUND
                        )

            return Response({"message": "Cập nhật thứ tự thành công"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)