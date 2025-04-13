# views.py
from django.http import HttpResponse
from services.google_drive_service import (
    is_file_in_zmusic_video_folder,
    get_file_metadata,
    download_file_from_drive
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class DownloadVideoView(APIView):
    def get(self, request, *args, **kwargs):
        video_id = request.GET.get('id')
        if not video_id:
            return Response(
                {'error': 'Missing video ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify file is in correct folder
            if not is_file_in_zmusic_video_folder(video_id):
                return Response(
                    {'error': 'File not in ZMusic-Video folder'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get file metadata for filename
            metadata = get_file_metadata(video_id)
            file_name = metadata.get('name', f"{video_id}.mp4")
            
            # Download file from Drive
            file_content = download_file_from_drive(video_id)
            
            # Create response with file
            response = HttpResponse(file_content, content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except Exception as e:
            logger.exception(f"Failed to download video: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )