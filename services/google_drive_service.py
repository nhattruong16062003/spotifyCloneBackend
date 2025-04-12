import io
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'zmusic-456605-3f7931d3cb29.json'

def get_drive_service():
    """
    Initialize and return the Google Drive service
    """
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)
    return service

def is_file_in_zmusic_video_folder(file_id):
    """
    Check if the file is located in the ZMusic-Video folder
    """
    service = get_drive_service()
    try:
        # Find the ZMusic-Video folder
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and name='ZMusic-Video'",
            fields="files(id, name)"
        ).execute()
        items = results.get('files', [])
        
        if not items:
            return False
            
        folder_id = items[0]['id']
        
        # Check if file is in the folder
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

