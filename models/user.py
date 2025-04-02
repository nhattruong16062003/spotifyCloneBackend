from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from .role import Role

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        role = extra_fields.pop('role', None)
        if not role:
            role, _ = Role.objects.get_or_create(name='user')

        user = self.model(email=email, username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        role, _ = Role.objects.get_or_create(name='admin')
        extra_fields.setdefault('role', role)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150,unique = True)
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=150, null=True,blank=True)
    is_ban = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_active_premium(self):
        """Lấy gói premium hiện tại của user (nếu có)"""
        from django.utils import timezone
        from .premium_subscription import PremiumSubscription
        return self.premium_subscriptions.filter(end_date__gt=timezone.now()).order_by('-end_date').first()
