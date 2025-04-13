# my_project/__init__.py

from __future__ import absolute_import, unicode_literals

# Đảm bảo Celery được khởi động khi Django khởi động
from .celery import app as celery_app

__all__ = ('celery_app',)
