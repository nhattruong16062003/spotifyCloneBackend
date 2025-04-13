import io
import logging
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from django.core.files.uploadedfile import TemporaryUploadedFile
from celery import shared_task
from django.db import models
from models.models import User,Video


logger = logging.getLogger(__name__)

# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
# SERVICE_ACCOUNT_FILE = 'zmusic-456605-3f7931d3cb29.json'

# Cập nhật scopes để hỗ trợ upload
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',  # Chỉ cần quyền upload và quản lý file được tạo
    'https://www.googleapis.com/auth/drive.readonly'  # Giữ quyền đọc
]


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'spotifyCloneBackend', 'zmusic-456605-3f7931d3cb29.json')


def get_drive_service():
    """
    Initialize and return the Google Drive service
    """
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)
    return service

# def is_file_in_zmusic_video_folder(file_id):
#     """
#     Check if the file is located in the ZMusic-Video folder
#     """
#     service = get_drive_service()
#     try:
#         # Find the ZMusic-Video folder
#         results = service.files().list(
#             q="mimeType='application/vnd.google-apps.folder' and name='ZMusic-Video'",
#             fields="files(id, name)"
#         ).execute()
#         items = results.get('files', [])
        
#         if not items:
#             return False
            
#         folder_id = items[0]['id']
        
#         # Check if file is in the folder
#         file = service.files().get(fileId=file_id, fields="parents").execute()
#         return 'parents' in file and folder_id in file['parents']
#     except Exception as e:
#         logger.error(f"Error checking file folder: {str(e)}")
#         return False

def is_file_in_zmusic_video_folder(file_id):
    """
    Check if the file is located in the ZMusic-Video folder
    """
    service = get_drive_service()
    try:
        # Lấy ID của thư mục ZMusic-Video
        folder_id = get_zmusic_video_folder_id()

        # Kiểm tra parents của file
        file = service.files().get(fileId=file_id, fields="parents").execute()
        return 'parents' in file and folder_id in file['parents']
    except Exception as e:
        logger.error(f"Error checking file folder: {str(e)}")
        return False

def get_file_metadata(file_id):
    """
    Get metadata for a file including size, mimeType and name
    """
    service = get_drive_service()
    try:
        metadata = service.files().get(
            fileId=file_id, 
            fields="size,mimeType,name"
        ).execute()
        return metadata
    except Exception as e:
        logger.error(f"Error getting file metadata: {str(e)}")
        raise Exception(f"Failed to get file metadata: {str(e)}")

def generate_stream(file_id, range_header=None):
    """
    Generate a streaming response for the video file
    """
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    
    if range_header:
        request.headers['Range'] = range_header

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    try:
        # Download the entire file or requested range
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        # Yield the content in chunks
        fh.seek(0)
        while True:
            chunk = fh.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            yield chunk
    except Exception as e:
        logger.error(f"Error during streaming: {str(e)}")
        raise
    finally:
        fh.close()


def get_zmusic_video_folder_id():
    """
    Tìm thư mục ZMusic-Video trên Google Drive.
    Nếu không tồn tại, tự động tạo thư mục mới và trả về folder_id.
    Hàm này được dùng trong upload_video_to_drive và is_file_in_zmusic_video_folder.
    """
    service = get_drive_service()
    try:
        # Tìm thư mục ZMusic-Video
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and name='ZMusic-Video'",
            fields="files(id, name)"
        ).execute()
        items = results.get('files', [])

        if items:
            return items[0]['id']

        # Nếu không tồn tại, tạo thư mục mới
        folder_metadata = {
            'name': 'ZMusic-Video',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        return folder.get('id')

    except Exception as e:
        logger.error(f"Error getting/creating ZMusic-Video folder: {str(e)}")
        raise


def upload_video_to_drive(file_stream, file_name, mime_type='video/mp4'):
    """
    Upload a video file to the ZMusic-Video folder on Google Drive using Resumable Upload.
    Args:
        file_stream: Django UploadedFile (InMemory or Temporary)
        file_name: Desired name of the file on Google Drive
        mime_type: MIME type of the file
    Returns:
        Google Drive file ID
    """
    service = get_drive_service()
    temp_path = None  # để lưu đường dẫn file tạm nếu cần ghi từ RAM

    try:
        # Xác định đường dẫn thực tế của file
        if isinstance(file_stream, TemporaryUploadedFile):
            file_path = file_stream.temporary_file_path()
        else:
            # Ghi file từ RAM ra đĩa
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_name) as tmp_file:
                for chunk in file_stream.chunks():
                    tmp_file.write(chunk)
                file_path = tmp_file.name
                temp_path = file_path

        # Metadata cho file trên Drive
        folder_id = get_zmusic_video_folder_id()
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # Khởi tạo resumable upload
        media = MediaFileUpload(
            file_path,
            mimetype=mime_type,
            resumable=True
        )

        # Tạo request upload với chunked upload
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                percent = int(status.progress() * 100)
                print(f"Đang upload: {percent}%")

        # Thiết lập quyền công khai
        service.permissions().create(
            fileId=response.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        logger.info(f"Uploaded video {file_name} with ID: {response.get('id')}")
        return response.get('id')

    except Exception as e:
        logger.error(f"Error uploading video to Drive: {str(e)}")
        raise

    finally:
        # Dọn dẹp file tạm nếu có
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)



def delete_video_from_drive(file_id):
    """
    Xóa video khỏi Google Drive bằng file_id.
    """
    service = get_drive_service()
    try:
        service.files().delete(fileId=file_id).execute()
        logger.info(f"Đã xóa video trên Google Drive với ID: {file_id}")
    except Exception as e:
        logger.error(f"Lỗi khi xóa video trên Google Drive (ID: {file_id}): {str(e)}")
        # Có thể raise lại nếu muốn rollback tiếp
