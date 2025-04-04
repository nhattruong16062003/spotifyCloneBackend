from django.db import transaction, IntegrityError
from models.models import ArtistCollab, Song, User

class ArtistCollabService:
    @staticmethod
    def create_artist_collabs(song_id, artist_ids):
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return None  # Không cần transaction vì chưa vào DB

        created_collabs = []

        try:
            with transaction.atomic():
                for artist_id in artist_ids:
                    try:
                        artist = User.objects.get(id=artist_id)
                        collab, created = ArtistCollab.objects.get_or_create(
                            user=artist,
                            song=song
                        )
                        if created:
                            created_collabs.append(collab)
                    except User.Exist:
                        raise ValueError(f"Artist with id {artist_id} does not exist")
                    except IntegrityError as e:
                        raise ValueError(f"Error creating collab for artist {artist_id}: {str(e)}")
                # Nếu thành công, trả về danh sách created_collabs
                return created_collabs

        except Exception:
            # Rollback tự động khi có exception, trả về None
            return None