from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from models.video import Video
from models.user import User
from rest_framework.views import APIView
from services.google_drive_service import (upload_video_to_drive,delete_video_from_drive)
from services.UploadService import UploadService
from django.db import transaction
import os
import tempfile
class VideoView(APIView):
        
        
    def post(self, request):
        image_url = None  # Khởi tạo để kiểm tra sau nếu cần xóa

        try:
            with transaction.atomic():
                
                title = request.POST.get('title')
                description = request.POST.get('description')
                video_file = request.FILES.get('videoFile')
                image_file = request.FILES.get('imageFile')

                # Upload video lên Google Drive
                video_id = upload_video_to_drive(
                    file_stream=video_file,
                    file_name=video_file.name
                )
                print("da vao ham upload video")

                # Upload ảnh lên AWS S3
                image_url = UploadService.upload_image_to_s3(image_file, f"images/{image_file.name}")

                # Lưu vào model Video
                video = Video.objects.create(
                    title=title,
                    description=description,
                    video_id=video_id,
                    image_path=image_url,
                    uploaded_by=request.user  # Giả sử user đã đăng nhập
                )
            return JsonResponse({
                'status': 'success',
                'video_id': video_id,
                'message': 'Video uploaded successfully',
                'video': {
                    'id': video.id,
                    'title': video.title,
                    'image_path': video.image_path
                }
            })
             
        except Exception as e:
            # Nếu ảnh đã upload thì tiến hành xóa ảnh trên AWS S3
            if image_url:
                try:
                    UploadService.delete_image_from_s3(image_url)
                    print(f"Đã xóa ảnh {image_url} khỏi S3 do có lỗi xảy ra.")
                except Exception as delete_error:
                    print(f"Lỗi khi xóa ảnh khỏi S3: {delete_error}")

            # Nếu đã upload video thì xóa khỏi Google Drive
            if video_id:
                try:
                    delete_video_from_drive(video_id)
                except Exception as delete_video_err:
                    logger.error(f"Lỗi khi xóa video khỏi Google Drive: {str(delete_video_err)}")

            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)