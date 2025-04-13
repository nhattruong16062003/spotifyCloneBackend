from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from services.google_drive_service import (
    is_file_in_zmusic_video_folder,
    get_file_metadata,
    generate_stream
)

logger = logging.getLogger(__name__)

class StreamVideoView(APIView):
    """
    API endpoint to stream videos from Google Drive with support for range requests (seeking)
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for video streaming
        """
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

            # Get file metadata
            metadata = get_file_metadata(video_id)
            file_size = int(metadata.get('size', 0))
            mime_type = metadata.get('mimeType', 'video/mp4')
            file_name = metadata.get('name', f"{video_id}.mp4")

            # Handle range requests
            range_header = request.META.get('HTTP_RANGE', '')
            start = 0
            end = file_size - 1
            status_code = status.HTTP_200_OK
            content_length = file_size

            if range_header:
                try:
                    ranges = range_header.replace('bytes=', '').split('-')
                    start = int(ranges[0])
                    if ranges[1]:
                        end = int(ranges[1])
                    end = min(end, file_size - 1)
                    content_length = end - start + 1
                    status_code = status.HTTP_206_PARTIAL_CONTENT
                except (ValueError, IndexError):
                    logger.warning(f"Invalid range header: {range_header}")

            # Create streaming response
            response = StreamingHttpResponse(
                streaming_content=generate_stream(video_id, range_header),
                content_type=mime_type,
                status=status_code
            )

            # Set response headers
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(content_length)
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, HEAD'
            response['Access-Control-Expose-Headers'] = 'Content-Length,Content-Range'

            if range_header and status_code == status.HTTP_206_PARTIAL_CONTENT:
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'

            return response

        except Exception as e:
            logger.exception(f"Failed to stream video: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    