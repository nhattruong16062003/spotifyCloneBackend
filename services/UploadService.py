import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
import uuid
from django.conf import settings
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

class UploadService:
    @staticmethod
    def upload_mp3_to_s3(file, file_name):
        SECRET_KEY=settings.SECRET_KEY
        
        # Tạo tên tệp duy nhất bằng UUID và giữ lại phần mở rộng của tệp gốc
        unique_id = uuid.uuid4().hex
        file_extension = os.path.splitext(file_name)[1]
        unique_file_name = f"{unique_id}{file_extension}"

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.MP3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.MP3_AWS_SECRET_ACCESS_KEY,
            region_name=settings.MP3_AWS_S3_REGION_NAME
        )

        try:
            # Tải tệp lên S3 với tên tệp duy nhất
            s3.upload_fileobj(file, settings.MP3_AWS_STORAGE_BUCKET_NAME, unique_file_name)
            file_url = f"{settings.MP3_AWS_CDN_URL}/{unique_file_name}"
            return file_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(e)
            return None
        
    
    @staticmethod
    def delete_file_from_s3(url):   
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.MP3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.MP3_AWS_SECRET_ACCESS_KEY,
            region_name=settings.MP3_AWS_S3_REGION_NAME
        )
        file_name=UploadService.get_filename_from_url(url)

        try:
            # Thực hiện xóa file trên S3
            response =s3.delete_object(Bucket=settings.MP3_AWS_STORAGE_BUCKET_NAME, Key=file_name)
            # Kiểm tra nếu không có lỗi, xem phản hồi của S3
            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 204:
                print(f"Da xoa am thanh: {file_name}")
                return True
            else:
                print(f"Xoa am thanh that bai, response: {response}")
                return False
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Loi xac thuc khi xoa am thanh: {e}")
            return False
        except Exception as e:
            print(f"Da xay ra loi khi xoa am thanh: {e}")
            return False
        

    # @staticmethod
    # def upload_image_to_s3(image, image_name):
    #     # Tạo tên tệp duy nhất bằng UUID và giữ lại phần mở rộng của tệp gốc
    #     unique_id = uuid.uuid4().hex
    #     file_extension = os.path.splitext(image_name)[1]
    #     unique_image_name = f"{unique_id}{file_extension}"

    #     s3 = boto3.client(
    #         's3',
    #         aws_access_key_id=settings.IMG_AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.IMG_AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.IMG_AWS_S3_REGION_NAME
    #     )

    #     try:
    #         # Nén ảnh trước khi upload
    #         image = Image.open(image)
    #         buffer = BytesIO()
    #         image.save(buffer, format='JPEG', quality=85)
    #         buffer.seek(0)

    #         # Tải ảnh lên S3 với tên tệp duy nhất
    #         s3.upload_fileobj(buffer, settings.IMG_AWS_STORAGE_BUCKET_NAME, unique_image_name)
    #         image_url = f"{settings.IMG_AWS_S3_CUSTOM_DOMAIN}/{unique_image_name}"
    #         return image_url
    #     except (NoCredentialsError, PartialCredentialsError) as e:
    #         print(e)
    #         return None
        

    #Thay đổi hàm để có thể upload ảnh dưới nhiều định dạng khác nhau
    @staticmethod
    def upload_image_to_s3(image, image_name):
        # Tạo tên tệp duy nhất bằng UUID và giữ lại phần mở rộng của tệp gốc
        unique_id = uuid.uuid4().hex
        file_extension = os.path.splitext(image_name)[1].lower()  # Lấy đuôi file và chuyển thành chữ thường
        unique_image_name = f"{unique_id}{file_extension}"

        # Khởi tạo client S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.IMG_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.IMG_AWS_SECRET_ACCESS_KEY,
            region_name=settings.IMG_AWS_S3_REGION_NAME
        )

        try:
            # Mở ảnh bằng Pillow
            img = Image.open(image)
            
            # Chuẩn bị buffer
            buffer = BytesIO()
            
            # Xác định định dạng dựa trên đuôi file
            if file_extension in ['.png']:
                # Giữ nguyên định dạng PNG, tối ưu hóa nếu cần
                img.save(buffer, format='PNG', optimize=True)
                content_type = 'image/png'
            elif file_extension in ['.jpg', '.jpeg']:
                # Chuyển RGBA sang RGB nếu cần, lưu dưới dạng JPEG
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(buffer, format='JPEG', quality=85)
                content_type = 'image/jpeg'
            else:
                # Mặc định dùng JPEG nếu định dạng không được hỗ trợ
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(buffer, format='JPEG', quality=85)
                content_type = 'image/jpeg'
                unique_image_name = f"{unique_id}.jpg"  # Đổi tên file nếu cần

            buffer.seek(0)

            # Tải ảnh lên S3 với tên tệp duy nhất và content type phù hợp
            s3.upload_fileobj(
                buffer,
                settings.IMG_AWS_STORAGE_BUCKET_NAME,
                unique_image_name,
                ExtraArgs={'ContentType': content_type}  # Đặt content type cho S3
            )
            
            # Trả về URL của ảnh
            image_url = f"{settings.IMG_AWS_CDN_URL}/{unique_image_name}"
            return image_url

        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"AWS credentials error: {e}")

            return None
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None


    @staticmethod
    def delete_image_from_s3(url):
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.IMG_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.IMG_AWS_SECRET_ACCESS_KEY,
            region_name=settings.IMG_AWS_S3_REGION_NAME
        )
        file_name=UploadService.get_filename_from_url(url)

        try:
            # Thực hiện xóa file trên S3
            response = s3.delete_object(Bucket=settings.IMG_AWS_STORAGE_BUCKET_NAME, Key=file_name)
            # Kiểm tra nếu không có lỗi, xem phản hồi của S3
            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 204:
                print(f"Da xoa anh: {file_name}")
                return True
            else:
                print(f"Xoa anh that bai, response: {response}")
                return False
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Loi xac thuc khi xoa anh: {e}")
            return False
        except Exception as e:
            print(f"Da xay ra loi khi xoa anh: {e}")
            return False
        
    @staticmethod
    def get_filename_from_url(url):
        # Phân tích URL
        parsed_url = urlparse(url)
        
        # Cắt tên file từ phần path của URL
        file_name = parsed_url.path.split('/')[-1]
        return file_name