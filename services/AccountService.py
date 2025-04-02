from PIL import Image
from io import BytesIO
from services.UploadService import UploadService



class AccountService:
    @staticmethod
    def update_user(user, data, files,image_path,action):
        """
        Cập nhật thông tin người dùng.
        """
        if(action == "change_image"):
            #Nếu trước đó người dùng có anh thì phải xóa trên aws
            if image_path is not None:
                UploadService.delete_image_from_s3(image_path)
            #Upload ảnh lên aws
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
        elif(action=="change_name"):
            # ảnh sẽ lấy đường dẫn ảnh cũ trong database 
            image_url = image_path
        elif(action == "delete_image"):
            if image_path is not None:
                UploadService.delete_image_from_s3(image_path)
                image_url = None
        user.name = data.get("name", user.name)
        user.image_path = image_url
        try:
            user.save()
        except Exception as e:
            # Nếu lưu thất bại, xóa ảnh đã upload lên S3 (nếu có)
            if image_url and "image_path" in files and action == "change_image":
                UploadService.delete_image_from_s3(image_name)
            raise Exception(f"USER_UPDATE_FAILED: {str(e)}")
        return user