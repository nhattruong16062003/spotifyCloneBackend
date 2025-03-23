from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.SongPlayHistoryService import SongPlayHistoryService  # Import service

class SongPlayHistoryView(APIView):
    def post(self, request):
        song_id = request.data.get("song_id")
        user_id = request.data.get("user_id")

        if not song_id or not user_id:
            return Response(
                {"error": "Both song_id and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Gọi service để lưu lịch sử phát nhạc
        SongPlayHistoryService.save_play_history(song_id, user_id)

        return Response({"message": "Play history updated successfully"}, status=status.HTTP_201_CREATED)
