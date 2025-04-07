from rest_framework import serializers
from models.artist_registration import ArtistRegistration

class ArtistRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistRegistration
        fields = '__all__'  
