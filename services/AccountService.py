from PIL import Image
from io import BytesIO
from services.UploadService import UploadService
from django.core.exceptions import PermissionDenied
from models.user import User
from api.serializers.UserSerializer import UserSerializer



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


    @staticmethod
    def ban_or_unban_user(user_to_update, action):
        """
        Xử lý việc ban hoặc mở khóa tài khoản người dùng.
        """
        if action == "ban-account":
            user_to_update.is_ban = True
            message_code = "USER_BANNED_SUCCESS"
            message = "User has been banned successfully."
        elif action == "unban-account":
            user_to_update.is_ban = False
            message_code = "USER_UNBANNED_SUCCESS"
            message = "User has been unbanned successfully."
        else:
            raise ValueError("Invalid action. Action must be 'ban-account' or 'unban-account'.")

        # Lưu trạng thái người dùng
        user_to_update.save()
        return message_code, message

    @staticmethod
    def get_user_info(user):
        """
        Lấy thông tin người dùng hiện tại.
        """
        if not user.is_authenticated:
            raise PermissionDenied("User is not authenticated.")
        
        return UserSerializer(user).data

    @staticmethod
    def get_all_users():
        """
        Lấy tất cả người dùng có role là artist hoặc user (dành cho admin).
        """
        users = User.objects.filter(role__id__in=[2, 3])
        return UserSerializer(users, many=True).data