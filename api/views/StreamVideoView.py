from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from services.google_drive_service import download_file  # Import hàm bạn đã viết

logger = logging.getLogger(__name__)

class StreamVideoView(APIView):
    """
    API stream video từ Google Drive về frontend, dùng OAuth 2.0
    """

    def get(self, request, *args, **kwargs):
        video_id = request.GET.get('id')
        if not video_id:
            return Response({'error': 'Missing video ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Gọi hàm để tải video từ Google Drive về (trả về BytesIO)
            file_stream = download_file(video_id)

            response = StreamingHttpResponse(
                streaming_content=file_stream,
                content_type='video/mp4'
            )
            response['Content-Disposition'] = f'inline; filename="{video_id}.mp4"'
            response['Cache-Control'] = 'no-cache'

            return response

        except Exception as e:
            logger.exception(f"Failed to stream video: {str(e)}")
            return Response({'error': 'Failed to stream video'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
