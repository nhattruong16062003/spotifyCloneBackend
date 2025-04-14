from pathlib import Path 
import os
import pymysql
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
from decouple import config

pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_CHARSET = 'utf-8'

load_dotenv()  # Load biến môi trường từ file .env

MP3_AWS_ACCESS_KEY_ID = os.getenv("MP3_AWS_ACCESS_KEY_ID")
MP3_AWS_SECRET_ACCESS_KEY = os.getenv("MP3_AWS_SECRET_ACCESS_KEY")
MP3_AWS_STORAGE_BUCKET_NAME = os.getenv("MP3_AWS_STORAGE_BUCKET_NAME")
MP3_AWS_S3_REGION_NAME = os.getenv("MP3_AWS_S3_REGION_NAME")

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MP3_AWS_S3_FILE_OVERWRITE = False  # Không ghi đè file trùng tên
MP3_AWS_QUERYSTRING_AUTH = False  # Loại bỏ token khỏi URL file
MP3_AWS_S3_CUSTOM_DOMAIN = f"https://{MP3_AWS_STORAGE_BUCKET_NAME}.s3.{MP3_AWS_S3_REGION_NAME}.amazonaws.com"

MP3_AWS_CDN_URL = os.getenv('MP3_AWS_CDN_URL')
IMG_AWS_CDN_URL = os.getenv('IMG_AWS_CDN_URL')

IMG_AWS_ACCESS_KEY_ID = os.getenv("IMG_AWS_ACCESS_KEY_ID")
IMG_AWS_SECRET_ACCESS_KEY = os.getenv("IMG_AWS_SECRET_ACCESS_KEY")
IMG_AWS_STORAGE_BUCKET_NAME = os.getenv("IMG_AWS_STORAGE_BUCKET_NAME")
IMG_AWS_S3_REGION_NAME = os.getenv("IMG_AWS_S3_REGION_NAME")

IMG_AWS_S3_FILE_OVERWRITE = False  # Không ghi đè file trùng tên
IMG_AWS_QUERYSTRING_AUTH = False  # Loại bỏ token khỏi URL file
IMG_AWS_S3_CUSTOM_DOMAIN = f"https://{IMG_AWS_STORAGE_BUCKET_NAME}.s3.{IMG_AWS_S3_REGION_NAME}.amazonaws.com"


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(8rp7n8*zmy88f)yjl$!al$2#td-%vm*cuvka9zh1gcg+o*f@b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = 'models.User'  # Đăng ký custom User model
# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django REST Framework
    'rest_framework',
    'rest_framework.authtoken', 
    'rest_framework_simplejwt',
    
    # Your apps
    'api',
    'models',
    'cores',
    'payments',
    'services',

    # Allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    

    # Corsheaders
    'corsheaders',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Allauth
    'allauth.account.middleware.AccountMiddleware',

    # Corsheaders
    'corsheaders.middleware.CorsMiddleware',

    # Thêm Middleware kiểm tra quyền truy cập theo Role
    'middleware.RoleCheckMiddleware.RoleCheckMiddleware',

    'middleware.PremiumCheckMiddleware.PremiumCheckMiddleware',

]


WSGI_APPLICATION = 'spotifyCloneBackend.wsgi.application'


ROOT_URLCONF = 'spotifyCloneBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Cấu hình cơ sở dữ liệu
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME', default='spotify_db'),
        'USER': config('DATABASE_USER', default='user'),
        'PASSWORD': config('DATABASE_PASSWORD', default='12345'),
        'HOST': config('DATABASE_HOST', default='db'),  # Dùng cho production
        'PORT': config('DATABASE_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',  # Thêm dòng này để đảm bảo mã hóa tiếng Việt
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Email settings (for sending activation email)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'zmusic2025.service@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


# Allauth settings
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication', 
)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}


# Corsheaders settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",  # Thêm localhost nếu cần
    # Thêm các nguồn gốc khác nếu cần
]


# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Tự động kiểm tra JWT
    ),
}

# Simple JWT settings
# SIMPLE_JWT = {
#     'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
#     'BLACKLIST_AFTER_ROTATION': True,
# }

# Lấy JWT_SECRET_KEY từ biến môi trường
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key")  # Dự phòng nếu không có biến môi trường

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": JWT_SECRET_KEY,  # Sử dụng secret key từ biến môi trường
}

ASGI_APPLICATION = 'spotifyCloneBackend.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        #DELOY MỎ CMT KHÔNG XÓA CODE NÀY
        "CONFIG": {
            "hosts": [("redis", 6379)],
        }, 
        # "CONFIG": {
        #     "hosts": [("127.0.0.1", 6379)],  # ← Sửa ở đây
        # },
    },
}




# Celery Configuration
# CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Sử dụng Redis làm message broker
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Lưu kết quả vào Redis
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Hoặc RabbitMQ
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'
CELERY_TASK_SOFT_TIME_LIMIT = 1800  # 30 phút
CELERY_TASK_TIME_LIMIT = 2000      # Hard limit
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
