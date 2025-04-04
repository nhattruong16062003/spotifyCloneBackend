from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils.crypto import get_random_string
from models.user import User
from services.UploadService import UploadService
from models.artist_registration import ArtistRegistration


class ArtistRegistrationService:
    @staticmethod
    def approve_artist(artist):
        """Phê duyệt nghệ sĩ và tạo tài khoản người dùng."""
        try:
            with transaction.atomic():
                print("Transaction started...")

                # Tạo mật khẩu ngẫu nhiên
                random_password = get_random_string(length=10)

                # Tạo User từ ArtistRegistration
                new_user = User.objects.create_user(
                    email=artist.email,
                    username=artist.email,
                    password=random_password,
                    name=artist.artist_name,
                    role_id=2
                )

                # Xóa các hình ảnh user đã đẩy lên AWS
                proof_images = artist.identity_proof.split(",") if artist.identity_proof else []
                artist_images = artist.artist_image.split(",") if artist.artist_image else []
                all_images = proof_images + artist_images

                for image_url in all_images:
                    if image_url.strip():
                        try:
                            image_name = image_url.split("/")[-1]
                            UploadService.delete_image_from_s3(image_name)
                            print(f"Deleted image from S3: {image_name}")
                        except Exception as delete_error:
                            print(f"Failed to delete image {image_url}: {str(delete_error)}")
                            continue

                # Gửi email thông báo phê duyệt
                subject = 'Your Artist Account is Approved!'
                message = f'Hello {artist.artist_name}, Your artist account has been approved. You can now log in using the credentials below:\n\n' \
                          f'Email: {artist.email}\nPassword: {random_password}\n\nPlease change your password after logging in.\n\n' \
                          f'If you have any questions, please contact us. \n\n Email: {settings.EMAIL_HOST_USER}\n\n Best regards,\nAdmin Team'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [artist.email]
                send_mail(subject, message, email_from, recipient_list)

                # Xóa yêu cầu khỏi bảng ArtistRegistration
                artist.delete()

                print("Transaction committed...")
                return {
                    "message": "Artist approved, images deleted, and account created successfully!"
                }

        except Exception as e:
            print(f"Transaction rolled back due to: {str(e)}")
            raise e

    @staticmethod
    def reject_artist(artist):
        """Từ chối nghệ sĩ và xóa yêu cầu."""
        try:
            with transaction.atomic():
                print("Transaction started...")

                # Lấy danh sách các URL từ artist_image và identity_proof
                artist_images = artist.artist_image.split(",") if artist.artist_image else []
                proof_images = artist.identity_proof.split(",") if artist.identity_proof else []
                all_images = artist_images + proof_images

                # Xóa từng ảnh trên S3
                for image_url in all_images:
                    if image_url.strip():
                        try:
                            image_name = image_url.split("/")[-1]
                            UploadService.delete_image_from_s3(image_name)
                            print(f"Deleted image from S3: {image_name}")
                        except Exception as delete_error:
                            print(f"Failed to delete image {image_url}: {str(delete_error)}")
                            continue

                # Gửi email thông báo từ chối
                subject = 'Your Artist Account is Rejected!'
                message = f'Hello {artist.artist_name}, Your artist account has been rejected: \n\n' \
                          f'If you have any questions, please contact us. \n\n Email: {settings.EMAIL_HOST_USER}\n\n Best regards,\nAdmin Team'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [artist.email]
                send_mail(subject, message, email_from, recipient_list)

                # Xóa yêu cầu khỏi bảng ArtistRegistration
                artist.delete()

                print("Transaction committed...")
                return {
                    "message": "Artist rejected and images deleted successfully!"
                }

        except Exception as e:
            print("Transaction rolled back...")
            raise e
