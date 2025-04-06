from models.models import User

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_users_by_role(role_id):
        try:
            users = User.objects.filter(role_id=role_id)
            return users
        except User.DoesNotExist:
            return None