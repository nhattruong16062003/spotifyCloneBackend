# views/VideoHistoryView.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import models
from models.models import Video, VideoPlayHistory

class VideoHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        video_id = request.data.get('video_id')
        
        # Kiểm tra video tồn tại
        video = get_object_or_404(Video, video_id=video_id)
        
        # Tạo bản ghi lịch sử phát
        VideoPlayHistory.objects.create(
            video=video,
            user=request.user,
            played_at=timezone.now()
        )
        
        # Trả về status mà không cần serializer
        return Response(status=status.HTTP_201_CREATED)
