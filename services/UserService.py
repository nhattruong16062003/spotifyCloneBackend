from models.models import User
from django.db.models import Q

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        
    @staticmethod
    def get_artists_by_name(search_query):
        return User.objects.filter(
            Q(name__icontains=search_query) & Q(role_id=2)
        ).order_by("name")[:5]
    
    @staticmethod
    def get_users_by_role(role_id):
        try:
            users = User.objects.filter(role_id=role_id)
            return users
        except User.DoesNotExist:
            return None