from PIL import Image
from io import BytesIO
from services.UploadService import UploadService


class AccountService:
    @staticmethod
    def update_user(user, data, files):
        """
        Cập nhật thông tin người dùng.
        """
        image_url = None

        # Kiểm tra nếu có file ảnh được upload
        if "image_path" in files:
            image = files["image_path"]
            original_image_name = image.name

            # Kiểm tra và chuyển đổi chế độ màu nếu cần
            try:
                img = Image.open(image)
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    buffer.seek(0)
                    image = buffer
            except Exception as e:
                raise Exception(f"IMAGE_PROCESSING_FAILED: {str(e)}")

            image_name = f"images/{original_image_name}"
            image_url = UploadService.upload_image_to_s3(image, image_name)
            if not image_url:
                raise Exception("IMAGE_UPLOAD_FAILED")
        elif data.get("image_path") == "":  # Nếu người dùng xóa ảnh
            image_url = None
        else:
            # Nếu không có ảnh mới, giữ nguyên ảnh hiện tại
            image_url = user.image_path

        # Cập nhật thông tin người dùng
        user.username = data.get("username", user.username)
        user.image_path = image_url

        # Lưu thay đổi
        try:
            user.save()
        except Exception as e:
            # Nếu lưu thất bại, xóa ảnh đã upload lên S3 (nếu có)
            if image_url and "image_path" in files:
                UploadService.delete_image_from_s3(image_name)
            raise Exception(f"USER_UPDATE_FAILED: {str(e)}")

        return user