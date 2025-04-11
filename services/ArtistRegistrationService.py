from django.conf import settings
from django.db import transaction
from django.utils.crypto import get_random_string
from models.user import User
from services.UploadService import UploadService
from models.artist_registration import ArtistRegistration
from services.EmailService import send_custom_email
from rest_framework.response import Response
from rest_framework import status

class ArtistRegistrationService:
    @staticmethod
    def approve_artist(artist_id):
        """Phê duyệt nghệ sĩ và tạo tài khoản người dùng."""
        try:
            with transaction.atomic():
                print("Transaction started...")

                #Kiểm tra lại xem artist còn tồn tại không
                #select_for_update nó sẽ lock hàng record đó tạm thời trong quá trình xử lý, tránh trường hợp admin khác duyệt cùng lúc.
                artist = ArtistRegistration.objects.select_for_update().filter(id=artist_id).first()
                if not artist:
                    return Response({
                        "error": True,
                        "error_code": "ARTIST_ALREADY_PROCESSED",
                        "message": "Yêu cầu đã được xử lý hoặc không tồn tại."
                    }, status=status.HTTP_409_CONFLICT)

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
                send_custom_email(
                    subject='Your Artist Account is Approved!',
                    username=artist.artist_name,
                    message=f'Your artist account has been approved. You can now log in using the credentials below:\n\n'
                            f'Email: {artist.email}\nPassword: {random_password}\n\n'
                            f'Please change your password after logging in.\n\n'
                            f'If you have any questions, please contact us at {settings.EMAIL_HOST_USER}.\n\n'
                            f'Best regards,\nAdmin Team',
                    link=None,
                    recipient_email=artist.email
                )


                # Xóa yêu cầu khỏi bảng ArtistRegistration
                artist.delete()

                print("Transaction committed...")
                return Response({
                    "error": False,
                    "error_code": "ARTIST_APPROVED_SUCCESS",
                    "message": "Artist approved successfully."
                }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Transaction rolled back due to: {str(e)}")
            return Response({
                "error": True,
                "error_code": "SERVER_ERROR",
                "message": "Đã xảy ra lỗi trong quá trình xử lý."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def reject_artist(artist_id):
        """Từ chối nghệ sĩ và xóa yêu cầu."""
        try:
            with transaction.atomic():
                print("Transaction started...")
                artist = ArtistRegistration.objects.select_for_update().filter(id=artist_id).first()
                if not artist:
                    return Response({
                        "error": True,
                        "error_code": "ARTIST_ALREADY_PROCESSED",
                        "message": "Yêu cầu đã được xử lý hoặc không tồn tại."
                    }, status=status.HTTP_409_CONFLICT)
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
                send_custom_email(
                    subject='Your Artist Account is Rejected!',
                    username=artist.artist_name,
                    message=f'Your artist account has been rejected.\n\n'
                            f'If you have any questions, please contact us at {settings.EMAIL_HOST_USER}.\n\n'
                            f'Best regards,\nAdmin Team',
                    link=None,
                    recipient_email=artist.email
                )

                # Xóa yêu cầu khỏi bảng ArtistRegistration
                artist.delete()

                print("Transaction committed...")
                return Response({
                    "error": False,
                    "error_code": "ARTIST_APPROVED_SUCCESS",
                    "message": "Artist rejected and images deleted successfully."
                }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Transaction rolled back...")
            return Response({
                "error": True,
                "error_code": "SERVER_ERROR",
                "message": "Đã xảy ra lỗi trong quá trình xử lý."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
