import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
import uuid
from django.conf import settings
from PIL import Image
from io import BytesIO

class UploadService:
    @staticmethod
    def upload_mp3_to_s3(file, file_name):
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
            file_url = f"{settings.MP3_AWS_S3_CUSTOM_DOMAIN}/{unique_file_name}"
            return file_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(e)
            return None

    @staticmethod
    def upload_image_to_s3(image, image_name):
        # Tạo tên tệp duy nhất bằng UUID và giữ lại phần mở rộng của tệp gốc
        unique_id = uuid.uuid4().hex
        file_extension = os.path.splitext(image_name)[1]
        unique_image_name = f"{unique_id}{file_extension}"

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.IMG_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.IMG_AWS_SECRET_ACCESS_KEY,
            region_name=settings.IMG_AWS_S3_REGION_NAME
        )

        try:
            # Nén ảnh trước khi upload
            image = Image.open(image)
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)

            # Tải ảnh lên S3 với tên tệp duy nhất
            s3.upload_fileobj(buffer, settings.IMG_AWS_STORAGE_BUCKET_NAME, unique_image_name)
            image_url = f"{settings.IMG_AWS_S3_CUSTOM_DOMAIN}/{unique_image_name}"
            return image_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(e)
            return None

    @staticmethod
    def delete_file_from_s3(file_name):
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.MP3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.MP3_AWS_SECRET_ACCESS_KEY,
            region_name=settings.MP3_AWS_S3_REGION_NAME
        )

        try:
            # Xóa tệp khỏi S3 bằng tên tệp
            s3.delete_object(Bucket=settings.MP3_AWS_STORAGE_BUCKET_NAME, Key=file_name)
            return True
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(e)
            return False