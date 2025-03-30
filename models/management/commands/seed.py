from django.core.management.base import BaseCommand
from faker import Faker
from models.models import User, Song, Subscription, Transaction, Playlist, PlaylistSong, PlaybackHistory,SongPlayHistory,Role
import random
from django.utils.timezone import now
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create fake roles
        roles = [
            Role(id=1, name="admin"),
            Role(id=2, name="artist"),
            Role(id=3, name="user")
        ]

        for role in roles:
            if not Role.objects.filter(id=role.id).exists():  # Kiểm tra xem role đã tồn tại chưa
                role.save()

        # Create fake users
        for _ in range(10):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                google_id=fake.uuid4(),
                role_id=fake.random_element(elements=[2, 3]),
                is_active=fake.random_element(elements=(True, False)),
                created_at=fake.date_time_this_year()
            )
            user.set_password('password123')  # Hash the password
            user.save()

        # Create fake songs
        for _ in range(20):
            song = Song.objects.create(
                title=fake.sentence(nb_words=3),
                user=User.objects.order_by('?').first(),
                description=fake.word(),
                genre=fake.word(),
                duration=fake.random_int(min=180, max=300),  # Duration in seconds
                mp3_path=fake.file_path(),
                image_path=fake.file_path(),
                uploaded_at=fake.date_time_this_year()
            )
            song.save()

        # Create fake subscriptions
        for user in User.objects.all():
            subscription = Subscription.objects.create(
                user=user,
                plan=fake.random_element(elements=('free', 'premium')),
                start_date=fake.date_time_this_year(),
                end_date=fake.date_time_this_year(),
                status=fake.random_element(elements=('active', 'expired'))
            )
            subscription.save()

        # Create fake transactions
        for user in User.objects.all():
            transaction = Transaction.objects.create(
                user=user,
                amount=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
                payment_method=fake.random_element(elements=('qr_code', 'vnpay', 'momo')),
                transaction_date=fake.date_time_this_year(),
                status=fake.random_element(elements=('pending', 'completed', 'failed'))
            )
            transaction.save()

        # Create fake playlists
        for user in User.objects.all():
            playlist = Playlist.objects.create(
                user=user,
                name=fake.sentence(nb_words=2),
                created_at=fake.date_time_this_year()
            )
            playlist.save()

       # Create fake playlist songs
        for playlist in Playlist.objects.all():
            songs = list(Song.objects.order_by('?')[:5])  # Lấy ngẫu nhiên 5 bài hát
            for index, song in enumerate(songs, start=1):  # Bắt đầu order từ 1
                if not PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                    PlaylistSong.objects.create(
                        playlist=playlist,
                        song=song,
                        order=index  # Gán thứ tự bài hát trong playlist
                    )

        # Create fake playback history
        for user in User.objects.all():
            for _ in range(10):
                playback_history = PlaybackHistory.objects.create(
                    user=user,
                    song=Song.objects.order_by('?').first(),
                    played_at=fake.date_time_this_year()
                )
                playback_history.save()

         # Create fake SongPlayHistory
        for user in User.objects.all():
            for _ in range(random.randint(5, 15)):  # Tạo từ 5-15 lượt nghe/người
                song = Song.objects.order_by('?').first()
                played_at = now() - timedelta(days=random.randint(0, 30))  # Chọn ngày ngẫu nhiên trong tháng

                song_play_history = SongPlayHistory.objects.create(
                    user=user,
                    song=song,
                    played_at=played_at
                )
                song_play_history.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database'))