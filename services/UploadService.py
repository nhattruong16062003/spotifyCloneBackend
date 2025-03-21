import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os

class UploadService:
    @staticmethod
    def upload_file_to_s3(file, file_name):
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME")
        )

        try:
            s3.upload_fileobj(file, os.getenv("AWS_STORAGE_BUCKET_NAME"), file_name)
            file_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{file_name}"
            return file_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(e)
            return None

    @staticmethod
    def delete_file_from_s3(file_name):
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME")
        )

        try:
            s3.delete_object(Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"), Key=file_name)
            return True
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(e)
            return False