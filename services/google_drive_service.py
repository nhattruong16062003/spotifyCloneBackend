import os
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'zmusic-456605-3f7931d3cb29.json' 

# Hàm để lấy dịch vụ Google Drive
def get_drive_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)
    return service

# Hàm kiểm tra xem file có thuộc thư mục "ZMusic-Video" không
def is_file_in_zmusic_video_folder(file_id):
    service = get_drive_service()

    # Tìm ID thư mục "ZMusic-Video"
    try:
        results = service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='ZMusic-Video'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No folder named "ZMusic-Video" found.')
            return False
        folder_id = items[0]['id']

        # Kiểm tra xem file có thuộc thư mục "ZMusic-Video" không
        file = service.files().get(fileId=file_id, fields="parents").execute()
        if 'parents' in file and folder_id in file['parents']:
            return True
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Hàm tải file từ Google Drive
def download_file(file_id):
    service = get_drive_service()

    if not is_file_in_zmusic_video_folder(file_id):
        raise Exception("The file is not in the 'ZMusic-Video' folder.")

    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()  # Tiến hành tải file

    file_stream.seek(0)  # Đặt lại con trỏ về đầu file
    return file_stream
