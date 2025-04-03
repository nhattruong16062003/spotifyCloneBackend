from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from services.UserService import UserService

class FindArtistCollab(APIView):
    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('name', '')
        artists = UserService.get_artists_by_name(search_query)
        artist_list = [
            {
                'id': artist.id,
                'name': artist.name,
                'email': artist.email,
                'image_path': artist.image_path,

            }
            for artist in artists
        ]
        return Response(artist_list, status=status.HTTP_200_OK)

