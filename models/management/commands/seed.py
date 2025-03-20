from django.core.management.base import BaseCommand
from faker import Faker
from models.models import User, Artist, Song, Subscription, Transaction, Playlist, PlaylistSong, PlaybackHistory

class Command(BaseCommand):
    help = 'Seed database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create fake users
        for _ in range(10):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                google_id=fake.uuid4(),
                role=fake.random_element(elements=('artist', 'user')),
                is_active=fake.random_element(elements=(True, False)),
                created_at=fake.date_time_this_year()
            )
            user.set_password('password123')  # Hash the password
            user.save()

        # Create fake artists
        for _ in range(5):
            artist = Artist.objects.create(
                name=fake.name(),
                bio=fake.text()
            )
            artist.save()

        # Create fake songs
        for _ in range(20):
            song = Song.objects.create(
                title=fake.sentence(nb_words=3),
                artist=Artist.objects.order_by('?').first(),
                album=fake.word(),
                genre=fake.word(),
                duration=fake.random_int(min=180, max=300),  # Duration in seconds
                file_path=fake.file_path(),
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
            for _ in range(5):
                song = Song.objects.order_by('?').first()
                if not PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                    playlist_song = PlaylistSong.objects.create(
                        playlist=playlist,
                        song=song
                    )
                    playlist_song.save()

        # Create fake playback history
        for user in User.objects.all():
            for _ in range(10):
                playback_history = PlaybackHistory.objects.create(
                    user=user,
                    song=Song.objects.order_by('?').first(),
                    played_at=fake.date_time_this_year()
                )
                playback_history.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database'))