from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Chỉ định cấu hình của dự án Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotifyCloneBackend.settings')

app = Celery('spotifyCloneBackend')

# Tải cấu hình Celery từ Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động tìm kiếm và đăng ký các tác vụ trong các ứng dụng Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
