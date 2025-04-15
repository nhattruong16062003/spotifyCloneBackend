# -*- coding: utf-8 -*-

import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from models.models import Role  # Điều chỉnh import theo cấu trúc dự án
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with initial user data'

    def handle(self, *args, **kwargs):
        # Tạo hoặc lấy các vai trò
        artist_role, _ = Role.objects.get_or_create(name='artist')

        # Danh sách người dùng để seed
        users_data = [
            {
                'email': 'anhtraisayhi@gmail.com',
                'username': 'anhtraisayhi@gmail.com',
                'password': 'anhtraisayhi12345@',
                'name': 'Anh Trai "SAY HI"',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': None,
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 11, 46, 16, 662495)),
            },
            {
                'email': 'phapkieu@gmail.com',
                'username': 'admiphapkieu@gmail.com',
                'password': 'Phapkieu12345@',
                'name': 'Pháp Kiều',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': None,
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 1, 25)),
            },
            {
                'email': 'isaac@gmail.com',
                'username': 'isaac@gmail.com',
                'password': 'Isaac12345@',
                'name': 'Isaac',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': None,
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 11, 54, 20, 315551)),
            },
            {
                'email': 'jsol@gmail.com',
                'username': 'jsol@gmail.com',
                'password': 'Jsol12345@',
                'name': 'JSOL',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'quanap@gmail.com',
                'username': 'quanap@gmail.com',
                'password': 'Quanap12345@',
                'name': 'Quân A.P',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'quangtrung@gmail.com',
                'username': 'quangtrung@gmail.com',
                'password': 'Quangtrung12345@',
                'name': 'Quang Trung',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'alihoangduong@gmail.com',
                'username': 'alihoangduong@gmail.com',
                'password': 'Alihoangduong12345@',
                'name': 'Ali Hoàng Dương',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'lambaongoc@gmail.com',
                'username': 'lambaongoc@gmail.com',
                'password': 'Lambaongoc12345@',
                'name': 'Lâm Bảo Ngọc',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'jmiko@gmail.com',
                'username': 'jmiko@gmail.com',
                'password': 'Jmiko12345@',
                'name': 'Jmi Ko',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'songluan@gmail.com',
                'username': 'songluan@gmail.com',
                'password': 'Songluan12345@',
                'name': 'Song Luân',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
            {
                'email': 'trandangduong@gmail.com',
                'username': 'trandangduong@gmail.com',
                'password': 'Trandangduong12345@',
                'name': 'Trần Đăng Dương',
                'role': artist_role,  
                'is_active': True,
                'is_ban': False,
                'image_path': 'https://d7q8y8k6ari3o.cloudfront.net/a3a4eb88cbc84946a8a92af9baac5f76.jpg',
                'created_at': timezone.make_aware(datetime.datetime(2025, 4, 13, 21, 3, 29)),
            },
        ]

        # Tạo người dùng
        for user_data in users_data:
            try:
                if not User.objects.filter(email=user_data['email']).exists():
                    user = User.objects.create_user(
                        email=user_data['email'],
                        username=user_data['username'],
                        password=user_data['password'],
                        role=user_data['role'],
                        name=user_data['name'],
                        is_active=user_data['is_active'],
                        is_ban=user_data['is_ban'],
                        image_path=user_data['image_path'],
                    )
                    # Cập nhật created_at
                    User.objects.filter(id=user.id).update(created_at=user_data['created_at'])
                    self.stdout.write(self.style.SUCCESS(f"Successfully created user: {user_data['email']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"User {user_data['email']} already exists"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating user {user_data['email']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))