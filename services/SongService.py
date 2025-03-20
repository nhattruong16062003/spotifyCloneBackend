from models.models import Song

class SongService:
    @staticmethod
    def add_song(data):
        song = Song.objects.create(**data)
        return song

    @staticmethod
    def update_song(song_id, data):
        try:
            song = Song.objects.get(id=song_id)
            for key, value in data.items():
                setattr(song, key, value)
            song.save()
            return song
        except Song.DoesNotExist:
            return None

    @staticmethod
    def delete_song(song_id):
        try:
            song = Song.objects.get(id=song_id)
            song.delete()
            return True
        except Song.DoesNotExist:
            return False